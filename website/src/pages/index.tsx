import React from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import CodeBlock from "@theme/CodeBlock";
import Link from "@docusaurus/Link";

import "../css/custom.css";

const heroCode = `from django.db import models

from blueprint.fields import FlexField
from blueprint.models import ContentModel


class Article(ContentModel):
    title = models.CharField(max_length=200)
    content = FlexField(ARTICLE_SCHEMA)`;

const attributes = [
  { name: "id", note: "UUID, auto" },
  { name: "created_at", note: "timestamp, auto" },
  { name: "modified_at", note: "timestamp, auto" },
  { name: "edited_by", note: "FK to user" },
];

const features = [
  {
    emoji: "🧩",
    title: "Composable base models",
    text: "UUID keys, timestamps, an editor reference, soft deletion, manual ordering and singletons — abstract bases you mix into your models with plain inheritance.",
  },
  {
    emoji: "📐",
    title: "JSON with a schema",
    text: "FlexField validates stored content against a JSON Schema, so editor-configurable content stays structured and validated at the data layer.",
  },
  {
    emoji: "🗑️",
    title: "Soft deletion",
    text: "Deleting stamps removed_at instead of dropping rows — instance and queryset deletes both — with separate managers for available objects.",
  },
  {
    emoji: "🔂",
    title: "Singletons",
    text: "Settings-style models guaranteed single-row at the database level, with a manager that creates or updates on write.",
  },
  {
    emoji: "🖼️",
    title: "Media library",
    text: "Media and Folder models plus MediaField and ManyMediaField, with a file_type hint that editors like Content Studio can pick up.",
  },
  {
    emoji: "🧭",
    title: "URL paths and tags",
    text: "A unique, normalized URL path field and a tag field that trims, lowercases and deduplicates — the small stuff, done right.",
  },
];

export default function Home() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout title="Home" description={siteConfig.tagline}>
      <header className="hero-dbp">
        <div className="container">
          <div>
            <h1>
              The CMS parts of Django.
              <br />
              Without the CMS.
            </h1>
            <p className="tagline">
              Django Blueprint provides the models and fields every content
              project rebuilds — composable abstract bases, schema-validated
              JSON fields and a media library. It stays a library: no views, no
              templates, no lock-in.
            </p>
            <div className="buttons">
              <Link
                className="button button--lg button-dbp-primary"
                to="/docs/getting-started"
              >
                Get started
              </Link>
              <Link
                className="button button--lg button-dbp-secondary"
                href="https://github.com/dwarsbit/django-blueprint"
              >
                GitHub
              </Link>
            </div>
          </div>
          <div className="hero-visual">
            <CodeBlock language="python">{heroCode}</CodeBlock>
            <div className="hero-attributes">
              {attributes.map((attribute) => (
                <div className="hero-attribute" key={attribute.name}>
                  <span className="name">{attribute.name}</span>
                  <span>from ContentModel</span>
                  <span className="auto">{attribute.note}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>
      <main>
        <section className="features-dbp">
          <div className="container">
            <h2 className="section-title">
              Common models, uncommon fields
            </h2>
            <div className="features-grid">
              {features.map((feature) => (
                <div className="feature-card" key={feature.title}>
                  <span className="emoji" aria-hidden="true">
                    {feature.emoji}
                  </span>
                  <h3>{feature.title}</h3>
                  <p>{feature.text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
