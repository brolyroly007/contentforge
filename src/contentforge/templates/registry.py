"""Built-in content templates (ported from ai-content-api)."""

from __future__ import annotations

from contentforge.templates.models import ContentTemplate, TemplateField

TEMPLATES: dict[str, ContentTemplate] = {}


def _register(t: ContentTemplate) -> None:
    TEMPLATES[t.id] = t


# ── 1. Blog Post ────────────────────────────────────────────────
_register(
    ContentTemplate(
        id="blog",
        name="Blog Post",
        description="Generate a well-structured blog post with SEO optimization.",
        category="marketing",
        fields=[
            TemplateField(name="topic", label="Topic", placeholder="e.g. AI trends in 2026"),
            TemplateField(
                name="tone",
                label="Tone",
                type="select",
                options=["professional", "casual", "academic", "conversational"],
                default="professional",
            ),
            TemplateField(
                name="word_count",
                label="Word count",
                type="number",
                default="800",
                required=False,
            ),
            TemplateField(
                name="keywords",
                label="SEO keywords",
                required=False,
                placeholder="comma-separated",
            ),
        ],
        system_prompt=(
            "You are an expert content writer and SEO specialist. "
            "Write well-structured, engaging blog posts using markdown formatting. "
            "Include a compelling title (H1), clear subheadings (H2/H3), "
            "and a natural flow from introduction to conclusion."
        ),
        user_prompt_template=(
            "Write a {tone} blog post about: {topic}\n\n"
            "Target approximately {word_count} words.\n"
            "{keywords_line}"
        ),
    )
)

# ── 2. Social Media Post ────────────────────────────────────────
_register(
    ContentTemplate(
        id="social",
        name="Social Media Post",
        description="Create platform-optimized social media content.",
        category="social",
        fields=[
            TemplateField(
                name="platform",
                label="Platform",
                type="select",
                options=["linkedin", "instagram", "twitter", "facebook"],
                default="linkedin",
            ),
            TemplateField(name="topic", label="Topic", placeholder="e.g. Remote work tips"),
            TemplateField(
                name="goal",
                label="Goal",
                type="select",
                options=["engagement", "awareness", "traffic", "conversion"],
                default="engagement",
            ),
            TemplateField(
                name="include_hashtags",
                label="Include hashtags",
                type="select",
                options=["yes", "no"],
                default="yes",
                required=False,
            ),
        ],
        system_prompt=(
            "You are a social media expert. Create platform-optimized posts following these rules:\n"
            "- Instagram: visual storytelling, use emojis, 2200 char max\n"
            "- LinkedIn: professional tone, industry insights, thought leadership\n"
            "- Twitter/X: concise, max 280 chars, punchy\n"
            "- Facebook: conversational, community-building, shareable"
        ),
        user_prompt_template=(
            "Create a {platform} post about: {topic}\n\n"
            "Goal: {goal}\n"
            "Include hashtags: {include_hashtags}"
        ),
    )
)

# ── 3. Email ────────────────────────────────────────────────────
_register(
    ContentTemplate(
        id="email",
        name="Email",
        description="Generate professional emails with subject lines.",
        category="email",
        fields=[
            TemplateField(
                name="type",
                label="Email type",
                type="select",
                options=["marketing", "cold-outreach", "newsletter", "follow-up", "announcement"],
                default="marketing",
            ),
            TemplateField(
                name="subject",
                label="Subject / context",
                placeholder="e.g. Product launch announcement",
            ),
            TemplateField(
                name="recipient",
                label="Recipient",
                placeholder="e.g. customers, leads, team",
                default="customers",
            ),
            TemplateField(
                name="cta",
                label="Call to action",
                required=False,
                placeholder="e.g. Sign up now",
            ),
        ],
        system_prompt=(
            "You are an email marketing expert. Write emails with:\n"
            "- A compelling subject line (output it first as **Subject:** ...)\n"
            "- Personalized greeting\n"
            "- Clear value proposition\n"
            "- Strong call-to-action\n"
            "Keep paragraphs short. Use markdown formatting."
        ),
        user_prompt_template=(
            "Write a {type} email.\n\n"
            "Context: {subject}\n"
            "Recipient: {recipient}\n"
            "Call to action: {cta}"
        ),
    )
)

# ── 4. Tweet Thread ─────────────────────────────────────────────
_register(
    ContentTemplate(
        id="tweet-thread",
        name="Tweet Thread",
        description="Create engaging Twitter/X threads.",
        category="social",
        fields=[
            TemplateField(name="topic", label="Topic", placeholder="e.g. Python tips"),
            TemplateField(
                name="count",
                label="Number of tweets",
                type="number",
                default="8",
            ),
            TemplateField(
                name="style",
                label="Style",
                type="select",
                options=["educational", "storytelling", "listicle", "controversial-take"],
                default="educational",
            ),
        ],
        system_prompt=(
            "You are a Twitter/X expert creating viral threads.\n"
            "Rules:\n"
            "- Tweet 1 (hook): bold statement or intriguing question\n"
            "- Each tweet: max 280 chars\n"
            "- Last tweet: CTA (follow, retweet, bookmark)\n"
            "- Number each tweet (1/, 2/, etc.)\n"
            "- Use line breaks between tweets"
        ),
        user_prompt_template=(
            "Create a {style} Twitter thread about: {topic}\n\n"
            "Length: {count} tweets"
        ),
    )
)

# ── 5. Ad Copy ──────────────────────────────────────────────────
_register(
    ContentTemplate(
        id="ad",
        name="Ad Copy",
        description="Generate ad copy optimized for specific platforms.",
        category="marketing",
        fields=[
            TemplateField(
                name="platform",
                label="Ad platform",
                type="select",
                options=["google-ads", "facebook-ads", "instagram-ads", "linkedin-ads"],
                default="google-ads",
            ),
            TemplateField(
                name="product",
                label="Product / service",
                placeholder="e.g. AI writing tool",
            ),
            TemplateField(
                name="audience",
                label="Target audience",
                placeholder="e.g. developers, marketers",
            ),
            TemplateField(
                name="usp",
                label="Unique selling point",
                required=False,
                placeholder="e.g. 10x faster content creation",
            ),
        ],
        system_prompt=(
            "You are a performance marketing copywriter.\n"
            "Platform guidelines:\n"
            "- Google Ads: 3 headlines (30 chars each), 2 descriptions (90 chars each)\n"
            "- Facebook/Instagram Ads: primary text, headline, description, CTA\n"
            "- LinkedIn Ads: intro (150 chars), headline, description\n"
            "Generate 3 ad variations."
        ),
        user_prompt_template=(
            "Create {platform} ad copy for:\n\n"
            "Product: {product}\n"
            "Audience: {audience}\n"
            "USP: {usp}\n\n"
            "Generate 3 ad variations."
        ),
    )
)

# ── 6. SEO Meta Tags ───────────────────────────────────────────
_register(
    ContentTemplate(
        id="seo",
        name="SEO Meta Tags",
        description="Generate optimized meta tags for web pages.",
        category="seo",
        fields=[
            TemplateField(
                name="keyword",
                label="Primary keyword",
                placeholder="e.g. ai tools",
            ),
            TemplateField(
                name="page_type",
                label="Page type",
                type="select",
                options=["blog-post", "landing-page", "product-page", "homepage"],
                default="blog-post",
            ),
            TemplateField(
                name="secondary_keywords",
                label="Secondary keywords",
                required=False,
                placeholder="comma-separated",
            ),
        ],
        system_prompt=(
            "You are an SEO specialist. Generate optimized meta tags:\n"
            "- Meta title: 50-60 chars, primary keyword near start\n"
            "- Meta description: 150-160 chars, include CTA\n"
            "- OG title: can be longer and more engaging\n"
            "- OG description: max 200 chars\n"
            "- 5 related long-tail keywords"
        ),
        user_prompt_template=(
            "Generate SEO meta tags for:\n\n"
            "Page type: {page_type}\n"
            "Primary keyword: {keyword}\n"
            "Secondary keywords: {secondary_keywords}"
        ),
        output_format="structured",
    )
)

# ── 7. Product Description ──────────────────────────────────────
_register(
    ContentTemplate(
        id="product",
        name="Product Description",
        description="Write compelling product descriptions that convert.",
        category="marketing",
        fields=[
            TemplateField(name="name", label="Product name", placeholder="e.g. AirPods Pro"),
            TemplateField(
                name="features",
                label="Key features",
                type="textarea",
                placeholder="e.g. noise cancel, spatial audio",
            ),
            TemplateField(
                name="audience",
                label="Target audience",
                required=False,
                placeholder="e.g. music lovers, professionals",
            ),
            TemplateField(
                name="tone",
                label="Tone",
                type="select",
                options=["premium", "friendly", "technical", "minimalist"],
                default="friendly",
                required=False,
            ),
        ],
        system_prompt=(
            "You are an expert copywriter specializing in product descriptions. "
            "Write benefit-focused copy that converts browsers into buyers. "
            "Use sensory language and highlight how features translate to benefits."
        ),
        user_prompt_template=(
            "Write a {tone} product description for: {name}\n\n"
            "Key features: {features}\n"
            "Target audience: {audience}"
        ),
    )
)

# ── 8. YouTube Description ──────────────────────────────────────
_register(
    ContentTemplate(
        id="youtube",
        name="YouTube Description",
        description="Create SEO-optimized YouTube video descriptions.",
        category="video",
        fields=[
            TemplateField(name="title", label="Video title"),
            TemplateField(
                name="summary",
                label="Video summary",
                type="textarea",
                placeholder="Brief overview of the video content",
            ),
            TemplateField(
                name="keywords",
                label="Keywords",
                required=False,
                placeholder="comma-separated",
            ),
            TemplateField(
                name="timestamps",
                label="Include timestamps",
                type="select",
                options=["yes", "no"],
                default="yes",
                required=False,
            ),
        ],
        system_prompt=(
            "You are a YouTube SEO expert. Structure descriptions as:\n"
            "1. Hook paragraph (2 lines, shown before 'Show more')\n"
            "2. Detailed summary\n"
            "3. Timestamps (if requested, use placeholder times)\n"
            "4. Links section (placeholder)\n"
            "5. Hashtags (3-5 relevant)\n"
            "Include keywords naturally. Max 5000 chars."
        ),
        user_prompt_template=(
            "Write a YouTube description for:\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Keywords: {keywords}\n"
            "Include timestamps: {timestamps}"
        ),
    )
)
