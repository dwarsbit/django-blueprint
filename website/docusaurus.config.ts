import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "Django Blueprint",
  tagline: "CMS building blocks for Django",
  url: "https://dwarsbit.github.io",
  baseUrl: "/django-blueprint/",
  organizationName: "dwarsbit",
  projectName: "django-blueprint",
  favicon: "img/logo.svg",

  onBrokenAnchors: "warn",

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: "warn",
    },
  },

  presets: [
    [
      "classic",
      {
        docs: {
          routeBasePath: "/",
          sidebarPath: "./sidebars.ts",
          editUrl:
            "https://github.com/dwarsbit/django-blueprint/edit/main/website",
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      defaultMode: "light",
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "Django Blueprint",
      logo: {
        alt: "Django Blueprint logo",
        src: "img/logo.svg",
      },
      items: [
        { label: "Getting started", to: "/getting-started", position: "left" },
        { label: "Models", to: "/models/content-models", position: "left" },
        { label: "Fields", to: "/fields/flex-field", position: "left" },
        {
          label: "Media library",
          to: "/media-library",
          position: "left",
        },
        {
          href: "https://github.com/dwarsbit/django-blueprint",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Docs",
          items: [
            { label: "Getting started", to: "/getting-started" },
            { label: "Models", to: "/models/content-models" },
            { label: "Fields", to: "/fields/flex-field" },
            { label: "Media library", to: "/media-library" },
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
      copyright: `Copyright © ${new Date().getFullYear()} Django Blueprint contributors. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.vsDark,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
