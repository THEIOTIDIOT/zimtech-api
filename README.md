# zimtechapi

- An api for my personal and company websites

## Cmds for migrating changes to data model

- to initialize db run - flask --app "zimtechapi:create_app('zimtechapi.config.TestingConfig')" db init
- to migrate db - flask --app "zimtechapi:create_app('zimtechapi.config.TestingConfig')" db migrate
- to upgrade db - flask --app "zimtechapi:create_app('zimtechapi.config.TestingConfig')" db upgrade
- to downgrade db - flask --app "zimtechapi:create_app('zimtechapi.config.TestingConfig')" db downgrade
