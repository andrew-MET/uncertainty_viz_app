module.exports = {
  apps: [
    {
      name: "sveltekit-app",
      cwd: "/path/to/your/sveltekit",
      script: "node",
      args: "build",
      env: {
        PORT: 3000
      }
    },
    {
      name: "fastapi-api",
      cwd: "/path/to/your/backend",
      script: "uvicorn",
      args: "app.main:app --host 127.0.0.1 --port 8000",
    }
  ]
};
