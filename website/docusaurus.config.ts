import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "Django Blueprint",
  tagline: "Common models and fields for CMS-like functionality in Django",
  favicon: "img/favicon.svg",
  url: "https://dwarsbit.github.io",
  baseUrl: "/django-blueprint/",
  organizationName: "dwarsbit",
  projectName: "django-blueprint",
  onBrokenLinks: "throw",
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: "warn",
    },
  },
  trailingSlash: false,
  themes: [],
  themeConfig: {
    colorMode: {
      defaultMode: "light",
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "Django Blueprint",
      logo: {
        alt: "Django Blueprint",
        src: "img/logo.svg",
      },
      items: [
        {
          label: "Docs",
          position: "left",
          to: "docs/intro",
        },
        {
          href: "https://github.com/dwarsbit/django-blueprint",
          label: "GitHub",
          position: "right",
        },
        {
          href: "https://pypi.org/project/django-blueprint/",
          label: "PyPI",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      copyright: `Copyright © ${new Date().getFullYear()} Leon van der Grient. Built with Django and Docusaurus.`,
      links: [
        {
          title: "Docs",
          items: [
            { label: "Introduction", to: "/docs/intro" },
            { label: "Getting started", to: "/docs/getting-started" },
            {
              label: "Media library",
              to: "/docs/media-library",
            },
          ],
        },
        {
          title: "Project",
          items: [
            {
              label: "GitHub",
              href: "https://github.com/dwarsbit/django-blueprint",
            },
            {
              label: "PyPI",
              href: "https://pypi.org/project/django-blueprint/",
            },
            {
              label: "Changelog",
              href: "https://github.com/dwarsbit/django-blueprint/blob/main/CHANGELOG.md",
            },
          ],
        },
      ],
    },
    prism: {
      additionalLanguages: ["bash", "json", "python", "yaml"],
    },
  } satisfies Preset.ThemeConfig,
  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          editUrl: "https://github.com/dwarsbit/django-blueprint/edit/main/website/",
          showLastUpdateTime: true,
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],
};

export default config;
