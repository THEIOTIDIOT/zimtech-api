#!/bin/bash
source venv/bin/activate
flask --app "zimtechapi:create_app('zimtechapi.config.ProductionConfig', ['api.benzimmer.us', 'blog.benzimmer.us'])" db upgrade
exec gunicorn -b :5000 -w 4 --access-logfile=- --error-logfile=- "zimtechapi:create_app('zimtechapi.config.ProductionConfig', ['api.benzimmer.us', 'blog.benzimmer.us'])"