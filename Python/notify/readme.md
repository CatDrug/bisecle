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
    BRANCH: ${CI_COMMIT_REF_NAME}
    DEBUG: fasle
    JIRA_PREFIX: ECOMFLS
    PROJECT_ID: ${CI_PROJECT_ID}
    TITLE: 🚀 Release progect
~~~