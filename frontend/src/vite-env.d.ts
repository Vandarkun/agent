/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  // 在这里添加其他环境变量
  // readonly VITE_SOME_OTHER_VAR: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
