import nodeResolve from '@rollup/plugin-node-resolve';
import typescript from '@rollup/plugin-typescript';
import json from '@rollup/plugin-json';
import terser from '@rollup/plugin-terser';
import commonjs from '@rollup/plugin-commonjs';

const plugins = [
  nodeResolve(),
  commonjs({
    include: 'node_modules/**'
  }),
  typescript({
    tsconfig: './tsconfig.json',
    noEmit: false,
  }),
  json(),
  terser()
];

export default [
  {
    input: 'src/irrigation-plus.ts',
    output: {
      dir: 'dist',
      format: 'iife',
      inlineDynamicImports: true,
      sourcemap: false,
    },
    plugins: [...plugins],
    context: 'window'
  },
  {
    // Tiny Lovelace card stub (auto-registered via add_extra_js_url) so it
    // loads on every page cheaply; it lazy-imports the impl bundle below only
    // when a card actually renders.
    input: 'src/irrigation-plus-card.ts',
    output: {
      dir: 'dist',
      format: 'iife',
      inlineDynamicImports: true,
      sourcemap: false,
    },
    plugins: [...plugins],
    context: 'window'
  },
  {
    // Backwards-compatibility shim registering the pre-#120 card tag. Served
    // ONLY when no foreign smart_irrigation integration is installed — see
    // panel.py; the decision is the backend's, not the browser's.
    input: 'src/irrigation-plus-card-legacy.ts',
    output: {
      dir: 'dist',
      format: 'iife',
      inlineDynamicImports: true,
      sourcemap: false,
    },
    plugins: [...plugins],
    context: 'window'
  },
  {
    // Heavy card implementation, lazy-loaded by the stub. Served as a separate
    // static file so non-card pages never download it.
    input: 'src/irrigation-plus-card-impl.ts',
    output: {
      dir: 'dist',
      format: 'iife',
      inlineDynamicImports: true,
      sourcemap: false,
    },
    plugins: [...plugins],
    context: 'window'
  },
];