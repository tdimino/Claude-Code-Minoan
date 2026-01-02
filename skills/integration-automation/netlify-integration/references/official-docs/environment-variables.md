[Skip to content](https://docs.netlify.com/build/functions/environment-variables/#_top)

# Environment variables and functions

Copy pageView as plain text

- Copy Markdown
- View as plain text

Netlify [environment variables](https://docs.netlify.com/build/environment-variables/overview) are accessible when you run Netlify Functions, Edge Functions, and On-demand Builders. This allows you to securely provide sensitive values for your functions to use while they run – values such as API keys and tokens.

This page describes how to create environment variables for functions, the specific read-only variables that are available to functions during runtime, and how to use environment variables within your serverless functions and edge functions.

## Declare variables

[Section titled “Declare variables”](https://docs.netlify.com/build/functions/environment-variables/#declare-variables "Copy link to this heading")

You can [declare and set environment variables](https://docs.netlify.com/build/environment-variables/get-started/#create-environment-variables) using the Netlify UI, CLI, or API for use with functions. If you have the option to set specific [scopes](https://docs.netlify.com/build/environment-variables/overview#scopes) for your environment variables, the scope must include **Functions** to be available to functions during runtime.

Note that environment variables declared in a Netlify configuration file (`netlify.toml`) are not available to functions.

Visit the [environment variables overview](https://docs.netlify.com/build/environment-variables/overview) to learn more about environment variables at Netlify.

## Netlify configuration variables

[Section titled “Netlify configuration variables”](https://docs.netlify.com/build/functions/environment-variables/#netlify-configuration-variables "Copy link to this heading")

By setting custom values for certain reserved environment variables, you can change some aspects of your functions.

- **`AWS_LAMBDA_JS_RUNTIME`:** value that sets the [Node.js runtime version for Netlify Functions](https://docs.netlify.com/build/functions/optional-configuration/?fn-language=js#node-js-version-for-runtime-2). This environment variable must be set using the Netlify UI, CLI, or API, and not with a Netlify configuration file (`netlify.toml`).

## Netlify read-only variables

[Section titled “Netlify read-only variables”](https://docs.netlify.com/build/functions/environment-variables/#netlify-read-only-variables "Copy link to this heading")

While Netlify offers a number of [configuration](https://docs.netlify.com/build/configure-builds/environment-variables#netlify-configuration-variables) and [read-only environment variables](https://docs.netlify.com/build/configure-builds/environment-variables#read-only-variables) during the build step, only the following read-only variables are available to functions during runtime.

Note that read-only environment variables are reserved in Netlify’s system. You can’t set or override these values manually.

### Functions

[Section titled “Functions”](https://docs.netlify.com/build/functions/environment-variables/#functions "Copy link to this heading")

The following read-only environment variables are available to serverless functions (including scheduled functions, background functions, and On-demand Builders):

- `SITE_NAME`: name of the site, its Netlify subdomain; for example, `petsof`.
- `SITE_ID`: unique ID for the site; for example, `1d01c0c0-4554-4747-93b8-34ce3448ab95`.
- `URL`: URL representing the main address to your site. It can be either a Netlify subdomain or your own custom domain if you set one; for example, `https://petsof.netlify.app` or`https://www.petsofnetlify.com`.

Also available are the [read-only, reserved runtime environment variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime) provided by AWS.

Note that other Netlify [read-only environment variables](https://docs.netlify.com/build/configure-builds/environment-variables#read-only-variables) are available when you use [Netlify Dev](https://docs.netlify.com/api-and-cli-guides/cli-guides/local-development) to help with local development, but only the above subset are available in all other environments.

### Edge Functions

[Section titled “Edge Functions”](https://docs.netlify.com/build/functions/environment-variables/#edge-functions "Copy link to this heading")

The following read-only environment variable is available to edge functions. The variable is provided by [Deno](https://deno.land/):

- `DENO_DEPLOYMENT_ID`: unique Deno ID of the deployment.

You can also leverage the [`Context` object](https://docs.netlify.com/build/edge-functions/api#netlify-specific-context-object) to access read-only information within your edge functions. For example, the `Context` object includes a `server` property with the `region` where the deployment is running and a Netlify-specific `site` property with the site’s `id`, `name`, and `url`.

## Overrides and limitations

[Section titled “Overrides and limitations”](https://docs.netlify.com/build/functions/environment-variables/#overrides-and-limitations "Copy link to this heading")

The general environment variable [overrides](https://docs.netlify.com/build/environment-variables/overview#overrides) and [limitations](https://docs.netlify.com/build/environment-variables/overview#limitations) apply to environment variables used with functions. Here are some additional limitations to note:

- Environment variables declared in a Netlify configuration file (`netlify.toml`) are not available to functions.
- Because Netlify Functions are powered by AWS Lambda, AWS’s [environment property limits](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html) apply to environment variables used with Netlify Functions. If you have the option to set specific [scopes](https://docs.netlify.com/build/environment-variables/overview#scopes) for your environment variables, you can adjust the scope of your variables to avoid hitting these limits.
- In addition to Netlify’s [read-only variables](https://docs.netlify.com/build/functions/environment-variables#netlify-read-only-variables), AWS’s [reserved environment variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime) are reserved in Netlify’s system. You can’t create environment variables with a key that’s reserved by a read-only variable. You also can’t set or override these values manually.
- Changes to environment variables for functions require a require a build and deploy to take effect.

## Access environment variables

[Section titled “Access environment variables”](https://docs.netlify.com/build/functions/environment-variables/#access-environment-variables "Copy link to this heading")

Once you declare environment variables for the **Functions** scope, you can access them in two different ways depending on if you are using [serverless functions](https://docs.netlify.com/build/functions/environment-variables/#functions-2) or [edge functions](https://docs.netlify.com/build/functions/environment-variables/#edge-functions-2). The following sections include examples of how to access these variables during runtime.

### Functions

[Section titled “Functions”](https://docs.netlify.com/build/functions/environment-variables/#functions-1 "Copy link to this heading")

In your serverless functions (including scheduled functions, background functions, and On-demand Builders), use the format `process.env.VARIABLE_NAME` to access environment variables available in the functions scope.

- [TypeScript](https://docs.netlify.com/build/functions/environment-variables/#tab-panel-119)
- [JavaScript](https://docs.netlify.com/build/functions/environment-variables/#tab-panel-120)

```
import type { Handler, HandlerEvent, HandlerContext } from "@netlify/functions";

const handler: Handler = async (event: HandlerEvent, context: HandlerContext) => {

const value = process.env.MY_IMPORTANT_VARIABLE;

return {

statusCode: 200,

body: JSON.stringify({ message: `Value of MY_IMPORTANT_VARIABLE is ${value}.`}),

};

};

export { handler };
```

```
exports.handler = async function (event, context) {

  const value = process.env.MY_IMPORTANT_VARIABLE;

  return {

    statusCode: 200,

    body: JSON.stringify({ message: `Value of MY_IMPORTANT_VARIABLE is ${value}.` }),

  };

};
```

### Edge Functions

[Section titled “Edge Functions”](https://docs.netlify.com/build/functions/environment-variables/#edge-functions-1 "Copy link to this heading")

Netlify provides environment variables to edge functions using the [`Netlify.env`](https://docs.netlify.com/build/edge-functions/api#netlify-global-object) API.

- **`get(key)`:** get the value of an environment variable
- **`toObject()`:** get all environment variables as an object

Note that you can’t use the `Netlify.env.set` and `Netlify.env.delete` methods to update environment variables from within edge functions. Instead, use the Netlify [`env` API endpoints](https://open-api.netlify.com/#tag/environmentVariables).

You can also leverage the Netlify-specific [context object](https://docs.netlify.com/build/edge-functions/api#netlify-specific-context-object) to access read-only information within your edge functions.

- [TypeScript](https://docs.netlify.com/build/functions/environment-variables/#tab-panel-121)
- [JavaScript](https://docs.netlify.com/build/functions/environment-variables/#tab-panel-122)

```
import type { Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {

const value = Netlify.env.get("MY_IMPORTANT_VARIABLE");

return new Response(`Value of MY_IMPORTANT_VARIABLE for ${context.site.name} is ${value}.`, {

headers: { "content-type": "text/html" },

});

};
```

```
export default async (request, context) => {

  const value = Netlify.env.get("MY_IMPORTANT_VARIABLE");

  return new Response(`Value of MY_IMPORTANT_VARIABLE for ${context.site.name} is ${value}.`, {

    headers: { "content-type": "text/html" },

  });

};
```

## More environment variables and functions resources

[Section titled “More environment variables and functions resources”](https://docs.netlify.com/build/functions/environment-variables/#more-environment-variables-and-functions-resources "Copy link to this heading")

- [Environment variables overview](https://docs.netlify.com/build/environment-variables/overview)
- [Build environment variables](https://docs.netlify.com/build/configure-builds/environment-variables)
- [Edge Functions example: Use environment variables](https://edge-functions-examples.netlify.app/example/environment)
- Verified Support Guide on [using an SSH key via environment variables during build](https://answers.netlify.com/t/support-guide-using-an-ssh-key-via-environment-variable-during-build/2457)
- [Netlify blog: How to use really long environment variables in Netlify Functions](https://www.netlify.com/blog/how-to-use-really-long-environment-variables-in-netlify-functions)

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
