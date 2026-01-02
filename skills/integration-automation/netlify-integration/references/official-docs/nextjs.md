[Skip to content](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#_top)

# Next.js on Netlify

Copy pageView as plain text

- Copy Markdown
- View as plain text

Netlify supports all major Next.js features with zero configuration, via our open-source [OpenNext adapter](https://github.com/opennextjs/opennextjs-netlify). This adapter is thoroughly tested with every Next.js release.

For Next.js versions prior to 13.5, visit the [legacy runtime](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/legacy-runtime/overview) page.

## Get started

[Section titled “Get started”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#get-started "Copy link to this heading")

If you have an existing Next.js app you’d like to deploy, push your code to a Git provider and connect it through the Netlify Dashboard.

When starting from scratch, the fastest way is to deploy our [Next.js platform starter template](https://github.com/netlify-templates/next-platform-starter) to your Netlify account.

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/netlify-templates/next-platform-starter)

## Key features

[Section titled “Key features”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#key-features "Copy link to this heading")

- **App Router:** Netlify fully supports the Next.js App Router, which supports more powerful nested layouts and React’s latest features, such as Server Components and Streaming.

- **Automatic fine-grained caching:** the adapter uses our [fine-grained caching primitives](https://docs.netlify.com/start/core-concepts/primitives#fine-grained-cache-control) to support the Next.js Full Route Cache and Data Cache. This means that static page responses are automatically cached at the edge and can be revalidated by path or by tag.

- **On-demand and time-based revalidation:** both the App Router and Pages Router support on-demand and time-based revalidation, allowing you to revalidate and regenerate content at any time after a deploy.

- **Image optimization:** the `next/image` component uses [Netlify Image CDN](https://docs.netlify.com/build/image-cdn/overview) by default, to ensure your images are optimized and served in the most efficient format.

- **Skew protection:** Netlify fully supports skew protection, to mitigate client-side errors for site visitors who are active when a new deployment goes live.


## Next.js support on Netlify

[Section titled “Next.js support on Netlify”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#nextjs-support-on-netlify "Copy link to this heading")

The following tables show you a comprehensive mapping of critical Next.js features and how Netlify supports them. Netlify supports new Next.js features as early as possible, but experimental features may not be fully stable yet.

| Next.js Feature | Support | Notes |
| --- | --- | --- |
| App Router | **✓** | Full Support |
| Server-Side Rendering (SSR) | **✓** | Full Support |
| Incremental Static Regeneration (ISR) | **✓** | Full Support |
| Static Site Generation (SSG) | **✓** | Full Support.<br>Pre-rendered pages are stored in Next.js route cache, and fetched from the route cache by a function invocation when first accessed after a deploy. |
| React Server Components | **✓** | Full Support |
| Server Actions | **✓** | Full Support |
| Response Streaming | **✓** | Full Support |
| asynchronous work with `next/after` | **✓** | Full Support.<br>Learn more in the [API reference.](https://docs.netlify.com/build/functions/api#waituntil) |
| Middleware | **✓** | Full support.<br>Implemented automatically via [Edge Functions](https://docs.netlify.com/build/edge-functions/overview). Note there are some [limitations](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#limitations), including a Node.js Middleware specific limitation. |
| Route Handlers | **✓** | Full Support |
| Image Optimization | **✓** | Full Support |
| Redirects and rewrites | **✓** | Full Support |
| Internationalization | **✓** | Full Support |
| Skew Protection | **✓** | Full Support |
| Draft Mode | **✓** | Full Support |
| Turbopack | **✓** | Full Support (dev and build) |
| Cache Components | **✓** | Full Support |

### How Netlify runs your Next.js app

[Section titled “How Netlify runs your Next.js app”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#how-netlify-runs-your-nextjs-app "Copy link to this heading")

Netlify automatically configures your project to support modern Next.js features out of the box. This is powered by our OpenNext adapter, an open source project that provisions the correct infrastructure for each part of your Next.js application without custom configuration.

We recommend that you don’t pin the adapter version. We actively maintain the adapter to support all Next.js versions starting from version 13.5 and, if you don’t pin the version, we will automatically update the adapter to the latest version on each project build for you.

#### What the adapter does

[Section titled “What the adapter does”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#what-the-adapter-does "Copy link to this heading")

When you deploy a Next.js project on Netlify, the adapter automatically:

- Provisions a serverless Netlify Function for handling: Server-Side Rendering (SSR), Incremental Static Regeneration (ISR), Partial Prerendering (PPR), Route handlers or API routes, and Server Actions.

- Provisions a Netlify Edge function for fast execution of Next.js Middleware at the edge.

- Configures the caching implementation for both the Next.js Full Route Cache and Data Cache, and handles tag-based and path-based revalidation.

- Enables image optimization with the Netlify Image CDN and `next/image`.


#### Compatibility and testing

[Section titled “Compatibility and testing”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#compatibility-and-testing "Copy link to this heading")

We verify compatibility with every new stable version of Next.js. Each release of the adapter is tested using:

- Our official end-to-end test suite.
- Additional integration tests with Netlify’s platform.
- Real-world deploys that we maintain.

## Skew protection

[Section titled “Skew protection”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#skew-protection "Copy link to this heading")

Each build of a Next.js site generates asset files (such as JavaScript bundles and CSS files). These files are automatically named with a unique hash derived from the build and file contents.

Additionally, the new deployment often comes with modified server-side code (e.g., React Server Components, Server Actions, Route handlers, etc.).

If a new production deployment goes live while visitors are in the middle of a session, it can cause several subtle issues:

- **Static asset 404s:** When navigating between pages, the client requests additional JavaScript bundles using identifiers that were provided with the initially loaded page. If those bundles no longer exist, the requests fail.

- **Failures on server-side calls:** Navigation, form submissions, and other dynamic features often fetch or post data. If responses rely on updated code that structures output differently, expects different inputs, or uses renamed paths, it can trigger unexpected browser errors.


These issues are difficult to consistently reason about and prevent without coordinated support from both the web framework and the deployment platform.

### How skew protection works

[Section titled “How skew protection works”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#how-skew-protection-works "Copy link to this heading")

Skew protection addresses these challenges by synchronizing client requests with the correct deployment:

- Each page load includes a unique deployment identifier.
- Next.js appends this identifier to subsequent client requests during navigation (until the next full page reload).
- Netlify CDN detects the given identifier and serves responses from the matching deployment — whether the current one or a previous one.

### Enabling skew protection

[Section titled “Enabling skew protection”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#enabling-skew-protection "Copy link to this heading")

Skew protection is **an opt-in feature**. To enable it:

1. Add an [environment variable](https://docs.netlify.com/build/environment-variables/overview) to your project configuration. Set the variable name to `NETLIFY_NEXT_SKEW_PROTECTION` and its value to `true`.

2. If you’re using a Next.js version _earlier than 14.1.4_, you also need to include the following flags in your `next.config.js` file:


```
/** @type {import('next').NextConfig} */

const nextConfig = {

  experimental: {

    useDeploymentId: true,

    // Optionally, use with Server Actions

    useDeploymentIdServerActions: true,

  },

};
```

3. Redeploy your project for the changes to take effect.

### Limitations of skew protection

[Section titled “Limitations of skew protection”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#limitations-of-skew-protection "Copy link to this heading")

- **No CLI deploy support:** Skew protection is not supported when deploying directly from the CLI.

- **No automatic support for fetch calls:** Next.js does not automatically add the deployment identifier to explicit `fetch` calls on the client. If you use `fetch` to call a route handler (or an API Route if using the Pages Router), the request is always served by the current deployment.


To adjust this behavior, you have two options:

1. Next.js 15.4.0 introduced a [new experimental feature](https://github.com/vercel/next.js/pull/78841) to handle these cases. Netlify supports this feature. However, that feature is not yet production-ready.
2. Alternatively, you can direct specific `fetch` calls to the correct deployment by adding a header:

```
fetch('/path', {

  headers: {

    'x-deployment-id': process.env.NEXT_DEPLOYMENT_ID

  },

});
```

Netlify detects this header and will rewrite the request to the correct deployment.

## Reverting to an older adapter version

[Section titled “Reverting to an older adapter version”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#reverting-to-an-older-adapter-version "Copy link to this heading")

To pin a specific version of the adapter:

1. Install the version you want in `package.json`:



```
npm install @netlify/plugin-nextjs@<version>
```

2. Add the plugin to your `netlify.toml`:



```
[[plugins]]

package = "@netlify/plugin-nextjs"
```


You’ll be opting out of automatic updates and newer architecture improvements maintained through OpenNext. To opt back in, remove `@netlify/plugin-nextjs` from your `package.json`.

## Limitations

[Section titled “Limitations”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#limitations "Copy link to this heading")

Open issues are documented in the [end-to-end test report page](https://runtime-e2e-report.netlify.app/).

- **Edge Runtime Support:** SSR pages using the edge runtime run in your functions region with the Node.js runtime, rather than in edge locations. No functionality is missing.
- **Rewrite Limitations:** Rewrites in Next.js configuration can’t point to static files in the public directory.
- **Middleware Execution Order:** Headers and redirects are evaluated after middleware, differing from stand-alone Next.js behavior.
- **Node.js Middleware:**
  - [C++ Addons](https://nodejs.org/api/addons.html) are not supported,
  - [Filesystem](https://nodejs.org/api/fs.html) is not supported.
- **Forms Integration:** Netlify Forms requires additional code when used with Next.js applications. [Learn more.](https://opennext.js.org/netlify/forms)

## More resources

[Section titled “More resources”](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/#more-resources "Copy link to this heading")

- [OpenNext adapter docs](https://opennext.js.org/netlify)
- [Next.js framework documentation](https://nextjs.org/docs/getting-started)
- [Netlify Connect JavaScript client](https://docs.netlify.com/build/data-and-storage/connect/access-data#use-the-connect-client)
- [Posts about Next.js in our blog](https://www.netlify.com/tags/nextjs/)

#### Did you find this doc useful?

Your feedback helps us improve our docs.

Do not fill in this field

What else would you like to tell us about this doc?

Send

Search
;
Clear

;

Ask Netlify AI

Get instant answers, powered by AI

;

## Help

- [;\\
\\
Go to support forums\\
\\
;](https://answers.netlify.com/)
- [;\\
\\
Contact support\\
\\
;](https://www.netlify.com/support/)
- [;\\
\\
Go to changelog\\
\\
;](https://netlify.com/changelog/)
- [;\\
\\
Contact sales\\
\\
;](https://www.netlify.com/contact/)

## Actions

;

Toggle theme

;

Escto close

Tabor↑↓to navigate

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)
