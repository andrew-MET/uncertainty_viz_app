module.exports = {
  apps: [
    {
      name: "sveltekit-app",
      cwd: "/home/andrewts/uncertainty_viz/app/uncertainty_viz_app/frontend",
      script: "node",
      args: "build",
      env: {
        NODE_ENV: "production",
        FASTAPI_BASE: "http://127.0.0.1:8000"
      }
    },
    {
      name: "fastapi-api",
      cwd: "/home/andrewts/uncertainty_viz/app/uncertainty_viz_app/backend",
      script: "/home/andrewts/uncertainty_viz/app/uncertainty_viz_app/backend/venv-api/bin/python",
      args: "-m uvicorn app.main:app --host 127.0.0.1 --port 8000",
    }
  ]
};
