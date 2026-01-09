param (
    [string]$Command
)

$ImageName = "tts-webapp"
$DockerId = "n301ix"
$FullImageName = "$DockerId/$ImageName"

if ($Command -eq "build") {
    Write-Host "Building Docker image..."
    docker-compose build
}
elseif ($Command -eq "up") {
    Write-Host "Starting application..."
    docker-compose up --build
}
elseif ($Command -eq "down") {
    Write-Host "Stopping application..."
    docker-compose down
}
elseif ($Command -eq "push") {
    Write-Host "Building..."
    # Force build to ensure latest code
    docker-compose build
    
    Write-Host "Tagging as $FullImageName..."
    # Tag the image defined in docker-compose (tts-webapp) to the hub name
    docker tag $ImageName "$FullImageName`:latest"
    
    Write-Host "Pushing to Docker Hub..."
    docker push "$FullImageName`:latest"
}
else {
    Write-Host "Usage: .\manage.ps1 [build|up|down|push]"
    Write-Host "  build: Build the image"
    Write-Host "  up   : Run the application"
    Write-Host "  down : Stop the application"
    Write-Host "  push : Build, tag, and push to Docker Hub"
}
