import { spawn } from 'child_process';
import { existsSync, mkdirSync } from 'fs';

const fastapiDir = './servers/fastapi';
const nextjsDir = './servers/nextjs';

// 创建必要的目录
const userDataDir = process.env.APP_DATA_DIRECTORY || './app_data';
if (!existsSync(userDataDir)) {
  mkdirSync(userDataDir, { recursive: true });
}

console.log('🚀 启动Presenton服务...');

// 启动FastAPI
const fastApiProcess = spawn('python', ['server.py', '--port', '8000'], {
  cwd: fastapiDir,
  stdio: 'inherit',
  env: process.env,
});

// 启动Next.js  
const nextjsProcess = spawn('npm', ['run', 'dev', '--', '-p', '3000'], {
  cwd: nextjsDir,
  stdio: 'inherit', 
  env: process.env,
});

// 启动Nginx
const nginxProcess = spawn('nginx', ['-g', 'daemon off;'], {
  stdio: 'inherit',
  env: process.env,
});

console.log('✅ 所有服务已启动');

// 保持进程运行
process.on('SIGTERM', () => {
  console.log('🛑 正在停止服务...');
  fastApiProcess.kill();
  nextjsProcess.kill();
  nginxProcess.kill();
  process.exit(0);
});

// 防止进程退出
setInterval(() => {}, 1000);