import gitlab
import requests
import os
import urllib3
import re
from jira import JIRA

# region variables
gitlab_url       = os.environ.get('URL_GITLAB')
gitlab_token     = os.environ.get('GITLAB_TOKEN')
gitlab_projectID = os.environ.get('PROJECT_ID')
jira_url         = os.environ.get('URL_JIRA')
jira_token       = os.environ.get('JIRA_TOKEN')
jira_prefix      = os.environ.get('JIRA_PREFIX')
mm_url           = os.environ.get('URL_MATTERMOST')
mm_token         = os.environ.get('MM_TOKEN')
mm_webhook_url   = mm_url + '/hooks/' + mm_token
mm_channel       = os.environ.get('CHANNEL')
releaseTag       = os.environ.get('RELEASE')
debug            = os.environ.get('DEBUG')
title            = os.environ.get('TITLE')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token, ssl_verify=False)
project = gl.projects.get(gitlab_projectID)

jira_options = {'server': jira_url, 'verify': False}
jira = JIRA(jira_options, basic_auth=('Git', jira_token ))

def get_previos_tag():
    tags = project.tags.list(all=True)
    filtered_tags = [tag for tag in tags if tag.name.startswith('v')]
    tags_sorted = sorted(filtered_tags, key=lambda t: t.commit['created_at'])

    # Search target tag index
    target_index = None
    for i, tag in enumerate(tags_sorted):
        if tag.name == releaseTag:
            target_index = i
            break

    # Check and display the previous tag
    if target_index is not None and target_index > 0:
        previous_tag = tags_sorted[target_index - 1]
    else:
        if target_index is None:
            raise Exception(f'Tag {releaseTag} not found.')
        else:
            raise Exception(f'Tag before {releaseTag} not found')
    return previous_tag.name

def extract_jira_tasks(commit_messages):

    pattern = re.compile(rf'{jira_prefix}-\d+')
    jira_tasks = set()

    for message in commit_messages:
        matches = pattern.findall(message)
        jira_tasks.update(matches)

    sortList = sorted(jira_tasks)    
    return sortList

def get_jira_issue_titles(issue_ids):
    issue_titles = {}
    for issue_id in issue_ids:
        try:
            issue = jira.issue(issue_id)
            # Проверка, является ли задача подзадачей
            if issue.fields.issuetype.subtask:
                continue
            issue_titles[issue_id] = issue.fields.summary
        except Exception as e:
            print(f"Failed to get task {issue_id}: {e}")
    
    return issue_titles

def send_to_mattermost(issue_titles):
    if not issue_titles:
        message = "There are no task IDs to submit."
    else:
        #message = "🚀 Релиз EPI " + releaseTag + "\n"
        message = f"{title} {releaseTag}\n"
        message += "\n".join([f"• {issue_id}: {title}" for issue_id, title in issue_titles.items()])

    if debug == 'true':
        print(message)
    else:
        payload = {"channel": mm_channel, "text": message}    
        response = requests.post(mm_webhook_url, json=payload)
        response.raise_for_status()  # If the request fails, throw an exception

def main():
    releaseTag_last = get_previos_tag()
    comparison = project.repository_compare(releaseTag_last, releaseTag)
    commits = comparison['commits']
    commit_messages = [commit['message'] for commit in commits]
    # Extract only unique identifiers
    filtered_jira_tasks = extract_jira_tasks(commit_messages)
    # Getting JIRA task names by IDs
    issue_titles = get_jira_issue_titles(filtered_jira_tasks)
    # Sending to mattermost
    send_to_mattermost(issue_titles)

if __name__ == "__main__":
    main()