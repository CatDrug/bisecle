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
gitlab_branch   = os.environ.get('BRANCH')
jira_url         = os.environ.get('URL_JIRA')
jira_token       = os.environ.get('JIRA_TOKEN')
jira_prefix      = os.environ.get('JIRA_PREFIX')
mm_url           = os.environ.get('URL_MATTERMOST')
mm_token         = os.environ.get('MM_TOKEN')
mm_webhook_url   = mm_url + '/hooks/' + mm_token
mm_channel       = os.environ.get('CHANNEL')
debug            = os.environ.get('DEBUG')
title            = os.environ.get('TITLE')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token, ssl_verify=False)
project = gl.projects.get(gitlab_projectID)

jira_options = {'server': jira_url, 'verify': False}
jira = JIRA(jira_options, basic_auth=('Git', jira_token ))

def get_last_merged_mr():
    merge_requests = project.mergerequests.list(
        target_branch=gitlab_branch, 
        state='merged', 
        order_by='updated_at', 
        sort='desc',
        get_all=False
    )
    return merge_requests[0]

def extract_version_from_title(merge_request_title):
    match = re.search(r'\d+(\.\d+)?', merge_request_title)
    if match:
        return match.group(0)
    else:
        return None

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
            # Checking if the task is a sub-task
            #if issue.fields.issuetype.subtask:
            #    continue
            issue_titles[issue_id] = issue.fields.summary
        except Exception as e:
            print(f"Failed to get task {issue_id}: {e}")
    
    return issue_titles

def send_to_mattermost(issue_titles, releaseTag):
    if not issue_titles and debug != 'true':
        message = "There are no task IDs to submit."
        return
    else:
        message = f"{title} {releaseTag}\n"
        message += "\n".join([f"• {issue_id}: {title}" for issue_id, title in issue_titles.items()])

    if debug == 'true':
        print(message)
    else:
        payload = {"channel": mm_channel, "text": message}    
        response = requests.post(mm_webhook_url, json=payload)
        response.raise_for_status()  # If the request fails, throw an exception

def main():
    last_mr = get_last_merged_mr()
    if last_mr:
        if 'RC' not in last_mr.labels:
            print("The last merged merge request does not have the 'RC' label.")
            return
    merge_request_id = last_mr.iid
    merge_request = project.mergerequests.get(merge_request_id)
    commits = merge_request.commits()
    commit_messages = [commit.title for commit in commits]
    version = extract_version_from_title(merge_request.title)
    if version is None:
        print("Error: Version not found")
        return
    releaseTag = 'v' +  version
    # Extract only unique identifiers
    filtered_jira_tasks = extract_jira_tasks(commit_messages)
    # Getting JIRA task names by IDs
    issue_titles = get_jira_issue_titles(filtered_jira_tasks)
    # Sending to mattermost
    send_to_mattermost(issue_titles, releaseTag)

if __name__ == "__main__":
    main()