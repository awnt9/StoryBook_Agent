set shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]

compose := "docker compose"
app_services := "frontend backend"

default: update

# Rebuild frontend/backend images and relaunch the full compose stack.
update:
    {{compose}} build --pull {{app_services}}
    {{compose}} up -d --force-recreate --remove-orphans
    {{compose}} ps

# Same as update, but bypass Docker build cache.
update-clean:
    {{compose}} build --pull --no-cache {{app_services}}
    {{compose}} up -d --force-recreate --remove-orphans
    {{compose}} ps

# Relaunch compose without rebuilding images.
restart:
    {{compose}} up -d --force-recreate --remove-orphans
    {{compose}} ps

# Show recent app logs.
logs:
    {{compose}} logs -f --tail=100 {{app_services}}
