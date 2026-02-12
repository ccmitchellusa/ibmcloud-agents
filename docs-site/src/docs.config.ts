import type { Config } from "./types/config";

const config: Config = {
  siteName: {
    prefix: 'IBM Cloud',
    postfixBold: 'MCP Agents'
  },
  tabTitle: 'IBM Cloud MCP Agents Docs',
  appUrl: 'http://localhost:5173/',
  githubUrl: 'https://github.com/ccmitchellusa/ibmcloud-agents/',
  footer: {
    copyright: {
      image: '/ibm-cloud-logo.png',
      notice: 'Copyright © 2025 IBM Corporation.'
    },
    content: {
      'Documentation': [
        {
          text: 'Get Started',
          external: false,
          url: '',
        },
      ],
      'Resources': [
        {
          text: 'IBM Blog',
          external: true,
          url: '',
        },
        {
          text: 'Model Context Protocol',
          external: true,
          url: '',
        },
        {
          text: 'MCP Agents',
          external: true,
          url: '',
        }
      ],
      'More': [
        {
          text: 'GitHub',
          external: true,
          url: ''
        }
      ]
    }
  }
}


export default config;
