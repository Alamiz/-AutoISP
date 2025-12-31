import { defineConfig, globalIgnores } from 'eslint/config'
import nextVitals from 'eslint-config-next/core-web-vitals'

const eslintConfig = defineConfig([
    ...nextVitals,
    // {
    //     rules: {
    //         "no-unused-vars": "warn",
    //     }
    // },
    globalIgnores([
        '.next/**',
        'out/**',
        'build/**',
        'next-env.d.ts',
        "**/*.d.ts", // Ignore type definition files
    ]),
])

export default eslintConfig