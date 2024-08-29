# Launch in gitlab
~~~yml
notify_mattermost:
  image: python:3.9
  script:
    - pip install jira requests python-gitlab
    - python script.py
  variables:
    URL_JIRA: "https://jira.com"
    URL_GITLAB: "https://gitlab.com"
    URL_MATTERMOST: "https://mattermost.com"
    CHANNEL: "releases"
    RELEASE: ${CI_COMMIT_TAG}
    DEBUG: true
    JIRA_PREFIX: PR
    PROJECT_ID: ${CI_PROJECT_ID}
    TITLE: 🚀 Release progect
~~~