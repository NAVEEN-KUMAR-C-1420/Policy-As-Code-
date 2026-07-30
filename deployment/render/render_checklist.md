# Render Checklist

- [ ] Connect Render to GitHub repository.
- [ ] Render Root Directory left blank (or `./`).
- [ ] Select `render.yaml` Blueprint or configure manually.
- [ ] Inject all required secrets in the Environment Variables tab.
- [ ] Configure Auto-Deploy to trigger ONLY on `main` branch pushes.
- [ ] Validate `/health` endpoint resolves to `200 OK` after deployment.
