module.exports = {
  apps: [
    {
      name: 'nextjs-app',
      script: 'npm',
      args: 'start',
      cwd: '/root/aso-rank-guard/web-app',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      error_file: '/var/log/pm2/nextjs-error.log',
      out_file: '/var/log/pm2/nextjs-out.log',
      log_file: '/var/log/pm2/nextjs-combined.log',
      time: true,
    },
  ],
}
