# Simulate the full presentation generation process

5db9f4b0-a585-4813-a1df-ec7aaecf3ee2 = "5db9f4b0-a585-4813-a1df-ec7aaecf3ee2"

Write-Host "Job ID: 5db9f4b0-a585-4813-a1df-ec7aaecf3ee2"
Write-Host ""

# Planning phase
Write-Host "📋 Planning..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/planning?status=in_progress&message=Analyzing%20prompt..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/planning?status=completed&message=Planning%20complete" -Method POST

# Research phase
Write-Host "🔍 Researching..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/research?status=in_progress&message=Gathering%20information..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/research?status=completed&message=Research%20complete" -Method POST

# Content generation
Write-Host "📝 Generating content..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/slides?status=in_progress&message=Creating%20slide%20content..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/slides?status=completed&message=Content%20generated" -Method POST

# Diagrams
Write-Host "📊 Creating diagrams..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/diagrams?status=in_progress&message=Generating%20diagrams..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/diagrams?status=completed&message=Diagrams%20created" -Method POST

# Animation
Write-Host "🎬 Generating animations..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/animation?status=in_progress&message=Creating%20animations..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/animation?status=completed&message=Animations%20complete" -Method POST

# PowerPoint
Write-Host "📄 Building PowerPoint..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/ppt?status=in_progress&message=Building%20presentation..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/ppt?status=completed&message=PowerPoint%20created" -Method POST

# PDF Export
Write-Host "📎 Exporting PDF..."
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/pdf?status=in_progress&message=Exporting%20PDF..." -Method POST
Start-Sleep -Seconds 1
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/pdf?status=completed&message=PDF%20exported" -Method POST

# Complete
Write-Host "✅ Complete!"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2/step/complete?status=completed&message=Presentation%20ready!" -Method POST

# Get final timeline
Write-Host ""
Write-Host "Final Timeline:"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/timeline/5db9f4b0-a585-4813-a1df-ec7aaecf3ee2" -Method GET | ConvertTo-Json -Depth 3
