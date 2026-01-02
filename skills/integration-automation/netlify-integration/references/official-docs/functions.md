[Skip to content](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#_top)

# Get started with functions

Copy pageView as plain text

- Copy Markdown
- View as plain text

This page will help you get started with Functions. It describes how to write your functions and route requests to them.

Select your function language:

TypeScriptJavaScriptGo

## Prepare project

[Section titled “Prepare project”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#prepare-project "Copy link to this heading")

Start by adding the `@netlify/functions` module to your project, which exports all the types you need to create type-safe functions.

```
npm install @netlify/functions
```

You don’t need any additional tooling or configuration to use TypeScript functions, but you can choose to provide your own [`tsconfig.json` file](https://www.typescriptlang.org/tsconfig) if you want to extend the base configuration in order to [rewrite import paths](https://www.typescriptlang.org/tsconfig#paths), for example.

Our build system will load any `tsconfig.json` files from your functions directory, the repository root directory, or the [base directory](https://docs.netlify.com/build/configure-builds/overview#definitions-1), if set.

## Create function file

[Section titled “Create function file”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#create-function-file "Copy link to this heading")

To add a serverless function to your project, create a TypeScript file in [your functions directory](https://docs.netlify.com/build/functions/optional-configuration#directory).

You can store your function file directly under the functions directory or in a subdirectory dedicated to the function. If you choose a subdirectory, the function entry file must be named `index` or have the same name as the subdirectory.

For example, any of the following files would create a function called `hello`:

- `netlify/functions/hello.mts`
- `netlify/functions/hello/hello.mts`
- `netlify/functions/hello/index.mts`

### Write a function

[Section titled “Write a function”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#write-a-function "Copy link to this heading")

A function file must be written using the [JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules) syntax and have a [default export](https://developer.mozilla.org/en-US/docs/web/javascript/reference/statements/export) with a handler function.

The handler function receives the following arguments:

- [A web platform `Request` object](https://developer.mozilla.org/en-US/docs/Web/API/Request) that represents the incoming HTTP request
- [A Netlify-specific `context` object](https://docs.netlify.com/build/functions/api#netlify-specific-context-object) with metadata related to the client and the site

For synchronous functions, the return value of the handler function may be used as the HTTP response to be delivered to the client.

### Synchronous function

[Section titled “Synchronous function”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#synchronous-function "Copy link to this heading")

A synchronous function lets you implement a traditional client/server interaction, where the connection is kept open until the function execution is finished, allowing the client to wait for a response before rendering a page or moving on to the next task.

The handler function should return a [`Response` object](https://developer.mozilla.org/en-US/docs/Web/API/Response) representing the HTTP response to be delivered to the client, including any [caching headers](https://docs.netlify.com/build/caching/caching-overview#supported-cache-control-headers) you want to set. If no value is returned, the client will receive an empty response with a 204 status code.

```
import type { Context } from "@netlify/functions";

export default async (req: Request, context: Context) => {

  return new Response("Hello, world!")

}
```

You can also use [`context.waitUntil`](https://docs.netlify.com/build/functions/api#netlify-specific-context-object) to handle background tasks without delaying the response. This is useful for logging, analytics, or other operations that don’t need to block the client.

```
import type { Context } from "@netlify/functions";

export default async (req: Request, context: Context) => {

  context.waitUntil(logRequest(req));

  return new Response("Hello, world!");

};

async function logRequest(req: Request) {

  await fetch("https://example.com/log", {

    method: "POST",

    body: JSON.stringify({ url: req.url, timestamp: Date.now() }),

    headers: { "Content-Type": "application/json" },

  });

}
```

Synchronous functions can stream data to clients as it becomes available, rather than returning a buffered payload at the end of the computation. This lets developers and frameworks create faster experiences by using streaming and partial hydration to get content and interactions in front of people as quickly as possible.

To stream a function’s response, return a [`ReadableStream`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream) as the `body` property of the `Response` object.

Examples

- [Manual stream](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#tab-panel-127)
- [OpenAI integration](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#tab-panel-128)
- [Groq integration](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#tab-panel-129)

```
export default async () => {

  const encoder = new TextEncoder();

  const formatter = new Intl.DateTimeFormat("en", { timeStyle: "medium" });

  const body = new ReadableStream({

    start(controller) {

      controller.enqueue(encoder.encode("<html><body><ol>"));

      let i = 0;

      const timer = setInterval(() => {

        controller.enqueue(

          encoder.encode(

            `<li>Hello at ${formatter.format(new Date())}</li>\n\n`

          )

        );

        if (i++ >= 5) {

          controller.enqueue(encoder.encode("</ol></body></html>"));

          controller.close();

          clearInterval(timer);

        }

      }, 1000);

    }

  });

  return new Response(body);

};
```

```
export default async () => {

  // Get the request from the request query string, or use a default

  const pie =

    event.queryStringParameters?.pie ??

    "something inspired by a springtime garden";

  // The response body returned from "fetch" is a "ReadableStream",

  // so you can return it directly in your streaming response

  const res = await fetch("https://api.openai.com/v1/chat/completions", {

    method: "POST",

    headers: {

      "Content-Type": "application/json",

      // Set this environment variable to your own key

      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`

    },

    body: JSON.stringify({

      model: "gpt-3.5-turbo",

      messages: [\
\
        {\
\
          role: "system",\
\
          content:\
\
            "You are a baker. The user will ask you for a pie recipe. You will respond with the recipe. Use markdown to format your response"\
\
        },\
\
        // Use "slice" to limit the length of the input to 500 characters\
\
        { role: "user", content: pie.slice(0, 500) }\
\
      ],

      // Use server-sent events to stream the response

      stream: true

    })

  });

  return new Response(body, {

    headers: {

      // This is the mimetype for server-sent events

      "content-type": "text/event-stream"

    }

  });

};
```

```
import Groq from "groq-sdk";

const client = new Groq({

  apiKey: process.env.GROQ_API_KEY

});

export default async () => {

  // Get the request from the request query string, or use a default

  const pie =

    event.queryStringParameters?.pie ??

    "something inspired by a springtime garden";

  // Create a transcription job

  const stream = await client.chat.completions.create({

    // The language model which will generate the completion.

    model: "llama3-8b-8192",

    messages: [\
\
      {\
\
        role: "system",\
\
        content:\
\
          "You are a baker. The user will ask you for a pie recipe. You will respond with the recipe. Use markdown to format your response"\
\
      },\
\
      // Use "slice" to limit the length of the input to 500 characters\
\
      { role: "user", content: pie.slice(0, 500) }\
\
    ],

    //

    // Optional parameters

    //

    // Controls randomness: lowering results in less random completions.

    // As the temperature approaches zero, the model will become deterministic

    // and repetitive.

    temperature: 0.5,

    // The maximum number of tokens to generate. Requests can use up to

    // 2048 tokens shared between prompt and completion.

    max_tokens: 1024,

    // Controls diversity via nucleus sampling: 0.5 means half of all

    // likelihood-weighted options are considered.

    top_p: 1,

    // A stop sequence is a predefined or user-specified text string that

    // signals an AI to stop generating content, ensuring its responses

    // remain focused and concise. Examples include punctuation marks and

    // markers like "[end]".

    stop: null,

    // If set, partial message deltas will be sent.

    stream: true

  });

  // Wrap the Stream<ChatCompletionChunk> in a ReadableStream

  const readableStream = new ReadableStream({

    async start(controller) {

      for await (const chunk of stream) {

        // Enqueue the chunk into the ReadableStream

        controller.enqueue(

          new TextEncoder().encode(chunk.choices[0]?.delta?.content || "")

        );

      }

      controller.close(); // Close the stream when it's done

    }

  });

  return new Response(readableStream, {

    headers: {

      // This is the mimetype for server-sent events

      "content-type": "text/event-stream"

    }

  });

};
```

When returning a stream, keep the following limitations in mind:

- 10 second execution limit. If the limit is reached, the response stops streaming.
- 20 MB response size limit. Responses larger than 20 MB cannot be streamed.

### Background function

[Section titled “Background function”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#background-function "Copy link to this heading")

This feature is available on [Credit-based plans, including Free, Personal, and Pro](https://www.netlify.com/pricing/?category=developer) and on [Enterprise](https://www.netlify.com/pricing/?category=enterprise) plans.

**If you are on the legacy Pro plan, this feature is available only until December 15, 2025.**

To keep using the feature, consider switching to an updated plan. [Learn more.](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-legacy-plans/legacy-pricing-plans/)

With background functions, the function invocation is placed into a queue and the client connection is terminated immediately. This pattern lets you perform longer-running operations without forcing clients to wait for a response.

The handler function does not need to return anything, as the client will always receive an empty response with a 202 status code. Any response returned by the handler function will be ignored.

```
import { Context } from "@netlify/functions";

export default async (req: Request, context: Context) => {

  await someLongRunningTask();

  console.log("Done");

};
```

To define a background function, the name of the function needs to have a `-background` suffix (for example, `netlify/functions/hello-background.mts` or `netlify/functions/hello-background/index.mts`).

## Route requests

[Section titled “Route requests”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#route-requests "Copy link to this heading")

Netlify automatically creates a dedicated endpoint for every function you create, using the format `https://<YOUR DOMAIN>/.netlify/functions/<FUNCTION NAME>`.

Additionally, you can configure the function to run on any path of your choice by defining a `path` property in the `config` export of your function.

```
import { Config, Context } from "@netlify/functions";

export default async (req: Request, context: Context) => {

  const { city, country } = context.params;

  return new Response(`You're visiting ${city} in ${country}!`);

};

export const config: Config = {

  path: "/travel-guide/:city/:country"

};
```

You can choose to run a function on one or more URL paths. To configure multiple paths, set the `path` property as an array.

```
import { Config } from "@netlify/functions";

export const config: Config = {

  path: ["/cats", "/dogs"]

};
```

You can leverage [the `URLPattern` syntax from the web platform](https://developer.mozilla.org/en-US/docs/Web/API/URL_Pattern_API) to define wildcards and named groups, which are matched against the incoming request URL and exposed to the function in the `context.params` object.

```
import { Config } from "@netlify/functions";

export const config: Config = {

  path: ["/sale/*", "/item/:sku"]

};
```

When needed, use `excludedPath` as an optional `URLPattern` exclusion to limit the routes matched by `path`. Must also start with `/`, for example `excludedPath = "/*.css"`. Accepts a single string or an array of strings.

```
import { Config } from "@netlify/functions";

export const config: Config = {

  path: "/product/*",

  excludedPath: ["/product/*.css", "/product/*.js"]

}
```

By default, a function runs for any requests to its configured paths regardless of whether or not static assets exist on those paths. To prevent the function from shadowing files on the CDN, set `preferStatic` to `true`.

```
import { Config } from "@netlify/functions";

export const config: Config = {

  path: ["/product/:sku", "/item/:sku"],

  preferStatic: true

};
```

## Environment variables

[Section titled “Environment variables”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#environment-variables "Copy link to this heading")

Netlify Functions have access to environment variables in the runtime environment via the `Netlify.env` global object.

```
import { Context } from "@netlify/functions";

export default async (req: Request, context: Context) => {

  const requestKey = req.headers.get("X-API-Key");

  const apiKey = Netlify.env.get("MY_API_KEY");

  if (requestKey === apiKey) {

    return new Response("Welcome!");

  }

  return new Response("Sorry, no access for you.", { status: 401 });

};
```

If you have the option to set specific scopes for your environment variables, the scope must include **Functions** to be available to functions during runtime.

You can also leverage [build environment variables](https://docs.netlify.com/build/configure-builds/environment-variables) to configure how Netlify builds your functions. For example, you can use an environment variable to set the Node.js version.

Learn more about how to set and use [environment variables with functions](https://docs.netlify.com/build/functions/environment-variables).

## Runtime

[Section titled “Runtime”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#runtime "Copy link to this heading")

Netlify Functions run in [Node.js](https://nodejs.org/), using the version [configured for your site](https://docs.netlify.com/build/functions/optional-configuration#node-js-version-for-runtime). Node.js version 18.0.0 is the minimum version required because functions use the [standard Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API), which was only added natively to Node.js in version 18.0.0.

### Module format

[Section titled “Module format”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#module-format "Copy link to this heading")

Node.js supports two distinct module formats with different capabilities and APIs: [ECMAScript modules](https://nodejs.org/api/esm.html) (or ES modules), an official standard format for JavaScript packages, and [CommonJS](https://nodejs.org/api/modules.html), a legacy format specific to Node.js.

The module format for each function will be determined by the file extension of its entry file:

- Functions with the `.mts` extension are always executed as ES modules
- Functions with the `.cts` extension are always executed as CommonJS
- Functions with the `.ts` extension are executed as ES modules if the closest `package.json` file has a `type` property with the value `module`; otherwise they are executed as CommonJS

Choosing a module format has implications on how you write your function, especially when it comes to importing npm packages:

- CommonJS functions cannot use a static `import` to load npm packages written as ES modules and must use a [dynamic import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)
- ES modules functions cannot use named imports (for example, `import { kebabCase } from "lodash"`) when referencing npm packages written in CommonJS, and should instead use a default import (for example, `import _ from "lodash"`)
- In ES modules, Node.js built-in primitives like `__dirname` and `__filename` are not available and should be replaced with [`import.meta.url`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import.meta)

## Lambda compatibility

[Section titled “Lambda compatibility”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#lambda-compatibility "Copy link to this heading")

Netlify Functions support an alternative API surface that is compatible with [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-nodejs.html). This may be useful if you’re looking to migrate Lambda workflows into Netlify with minimal refactoring required.

To opt-in, your handler function must be exported using a `handler` named export.

```
import type { Handler } from "@netlify/functions";

export const handler: Handler = async (event, context) => {

  return {

    body: JSON.stringify({ message: "Hello World" }),

    statusCode: 200,

  }

}
```

For more information about this API, refer to [Lambda compatibility](https://docs.netlify.com/build/functions/lambda-compatibility).

## Test locally

[Section titled “Test locally”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#test-locally "Copy link to this heading")

To streamline writing and testing your functions on Netlify, run a local development environment with [Netlify Dev](https://docs.netlify.com/api-and-cli-guides/cli-guides/local-development/). This feature of Netlify CLI includes tools for local function development through a simulated Netlify production environment. The `netlify dev` command starts a framework server if a framework is detected and handles redirects, proxy rules, environment variables, and Netlify Functions.

By default, the `geo` location used is the location of your local environment. To override this to a default mock location of San Francisco, CA, USA, use the `--geo=mock` flag. To mock a specific country, use `--geo=mock --country=` with a two-letter country code. For more information about the `--geo` flag, visit the [CLI docs](https://cli.netlify.com/commands/dev/).

## Next steps

[Section titled “Next steps”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#next-steps "Copy link to this heading")

Push your function source files to your Git provider for continuous deployment where Netlify’s build system automatically detects, builds, and deploys your functions. For more control over the process, learn about [other workflows for deploying your functions](https://docs.netlify.com/build/functions/deploy/) including custom builds with continuous deployment and manual deploys with the Netlify CLI or API.

Monitor function [logs](https://docs.netlify.com/build/functions/logs/) and [metrics](https://docs.netlify.com/manage/monitoring/function-metrics/) in the Netlify UI to observe and help troubleshoot your deployed functions.

Netlify function logs are found in the Netlify UI. You can also stream Netlify function logs to the console with the [Netlify CLI](https://cli.netlify.com/commands/logs/#logsfunction).

## Create function file

[Section titled “Create function file”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#create-function-file-1 "Copy link to this heading")

To add a serverless function to your project, create a JavaScript file in [your functions directory](https://docs.netlify.com/build/functions/optional-configuration#directory) following the instructions below for naming and coding your function. Netlify will access the functions directory during every build, preparing and deploying each supported code file as a function.

You can store your function file directly under the functions directory or in a subdirectory dedicated to the function. If you choose a subdirectory, the function entry file must be named `index` or have the same name as the subdirectory.

For example, any of the following files would create a function called `hello`:

- `netlify/functions/hello.mjs`
- `netlify/functions/hello/hello.mjs`
- `netlify/functions/hello/index.mjs`

### Write a function

[Section titled “Write a function”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#write-a-function-1 "Copy link to this heading")

A function file must be written using the [JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules) syntax and have a [default export](https://developer.mozilla.org/en-US/docs/web/javascript/reference/statements/export) with a handler function.

The handler function receives the following arguments:

- [A web platform `Request` object](https://developer.mozilla.org/en-US/docs/Web/API/Request) that represents the incoming HTTP request
- [A Netlify-specific `context` object](https://docs.netlify.com/build/functions/api#netlify-specific-context-object) with metadata related to the client and the site

For synchronous functions, the return value of the handler function may be used as the HTTP response to be delivered to the client.

### Synchronous function

[Section titled “Synchronous function”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#synchronous-function-1 "Copy link to this heading")

A synchronous function lets you implement a traditional client/server interaction, where the connection is kept open until the function execution is finished, allowing the client to wait for a response before rendering a page or moving on to the next task.

The handler function should return a [`Response` object](https://developer.mozilla.org/en-US/docs/Web/API/Response) representing the HTTP response to be delivered to the client. If no value is returned, the client will receive an empty response with a 204 status code.

```
export default async (req, context) => {

  return new Response("Hello, world!");

};
```

Synchronous functions can stream data to clients as it becomes available, rather than returning a buffered payload at the end of the computation. This lets developers and frameworks create faster experiences by using streaming and partial hydration to get content and interactions in front of people as quickly as possible.

To stream a function’s response, return a [`ReadableStream`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream) as the `body` property of the `Response` object.

Examples

- [Manual stream](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#tab-panel-130)
- [OpenAI integration](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#tab-panel-131)

```
export default async () => {

  const encoder = new TextEncoder();

  const formatter = new Intl.DateTimeFormat("en", { timeStyle: "medium" });

  const body = new ReadableStream({

    start(controller) {

      controller.enqueue(encoder.encode("<html><body><ol>"));

      let i = 0;

      const timer = setInterval(() => {

        controller.enqueue(

          encoder.encode(

            `<li>Hello at ${formatter.format(new Date())}</li>\n\n`

          )

        );

        if (i++ >= 5) {

          controller.enqueue(encoder.encode("</ol></body></html>"));

          controller.close();

          clearInterval(timer);

        }

      }, 1000);

    }

  });

  return new Response(body);

};
```

```
export default async () => {

  // Get the request from the request query string, or use a default

  const pie =

    event.queryStringParameters?.pie ??

    "something inspired by a springtime garden";

  // The response body returned from "fetch" is a "ReadableStream",

  // so you can return it directly in your streaming response

  const res = await fetch("https://api.openai.com/v1/chat/completions", {

    method: "POST",

    headers: {

      "Content-Type": "application/json",

      // Set this environment variable to your own key

      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`

    },

    body: JSON.stringify({

      model: "gpt-3.5-turbo",

      messages: [\
\
        {\
\
          role: "system",\
\
          content:\
\
            "You are a baker. The user will ask you for a pie recipe. You will respond with the recipe. Use markdown to format your response"\
\
        },\
\
        // Use "slice" to limit the length of the input to 500 characters\
\
        { role: "user", content: pie.slice(0, 500) }\
\
      ],

      // Use server-sent events to stream the response

      stream: true

    })

  });

  return new Response(body, {

    headers: {

      // This is the mimetype for server-sent events

      "content-type": "text/event-stream"

    }

  });

};
```

When returning a stream, keep the following limitations in mind:

- 10 second execution limit. If the limit is reached, the response stops streaming.
- 20 MB response size limit. Responses larger than 20 MB cannot be streamed.

### Background function

[Section titled “Background function”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#background-function-1 "Copy link to this heading")

This feature is available on [Credit-based plans, including Free, Personal, and Pro](https://www.netlify.com/pricing/?category=developer) and on [Enterprise](https://www.netlify.com/pricing/?category=enterprise) plans.

**If you are on the legacy Pro plan, this feature is available only until December 15, 2025.**

To keep using the feature, consider switching to an updated plan. [Learn more.](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-legacy-plans/legacy-pricing-plans/)

With background functions, the function invocation is placed into a queue and the client connection is terminated immediately. This pattern lets you perform longer-running operations without forcing clients to wait for a response.

The handler function does not need to return anything, as the client will always receive an empty response with a 202 status code. Any response returned by the handler function will be ignored.

```
export default async (req, context) => {

  await someLongRunningTask();

  console.log("Done");

};
```

To define a background function, the name of the function needs to have a `-background` suffix (for example, `netlify/functions/hello-background.mjs` or `netlify/functions/hello-background/index.mjs`).

## Route requests

[Section titled “Route requests”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#route-requests-1 "Copy link to this heading")

Netlify automatically creates a dedicated endpoint for every function you create, using the format `https://<YOUR DOMAIN>/.netlify/functions/<FUNCTION NAME>`.

Additionally, you can configure the function to run on any path of your choice by defining a `path` property in the `config` export of your function.

```
export default async (req, context) => {

  const { city, country } = context.params;

  return new Response(`You're visiting ${city} in ${country}!`);

};

export const config = {

  path: "/travel-guide/:city/:country"

};
```

You can choose to run a function on one or more URL paths. To configure multiple paths, set the `path` property as an array.

```
export const config = {

  path: ["/cats", "/dogs"]

};
```

You can leverage [the `URLPattern` syntax from the web platform](https://developer.mozilla.org/en-US/docs/Web/API/URL_Pattern_API) to define wildcards and named groups, which are matched against the incoming request URL and exposed to the function in the `context.params` object.

```
export const config = {

  path: ["/sale/*", "/item/:sku"]

};
```

When needed, use `excludedPath` as an optional `URLPattern` exclusion to limit the routes matched by `path`. Must also start with `/`, for example `excludedPath = "/*.css"`. Accepts a single string or an array of strings.

```
export const config = {

  path: "/product/*",

  excludedPath: ["/product/*.css", "/product/*.js"]

}
```

By default, a function runs for any requests to its configured paths regardless of whether or not static assets exist on those paths. To prevent the function from shadowing files on the CDN, set `preferStatic` to `true`.

```
export const config = {

  path: ["/product/:sku", "/item/:sku"],

  preferStatic: true

};
```

## Environment variables

[Section titled “Environment variables”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#environment-variables-1 "Copy link to this heading")

Netlify Functions have access to environment variables in the runtime environment via the `Netlify.env` global object.

```
export default async (req, context) => {

  const requestKey = req.headers.get("X-API-Key");

  const apiKey = Netlify.env.get("MY_API_KEY");

  if (requestKey === apiKey) {

    return new Response("Welcome!");

  }

  return new Response("Sorry, no access for you.", { status: 401 });

};
```

If you have the option to set specific scopes for your environment variables, the scope must include **Functions** to be available to functions during runtime.

You can also leverage [build environment variables](https://docs.netlify.com/build/configure-builds/environment-variables) to configure how Netlify builds your functions. For example, you can use an environment variable to set the Node.js version.

Learn more about how to set and use [environment variables with functions](https://docs.netlify.com/build/functions/environment-variables).

## Runtime

[Section titled “Runtime”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#runtime-1 "Copy link to this heading")

Netlify Functions run in [Node.js](https://nodejs.org/), using the version [configured for your site](https://docs.netlify.com/build/functions/optional-configuration#node-js-version-for-runtime). Node.js version 18.0.0 is the minimum version required because functions use the [standard Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API), which was only added natively to Node.js in version 18.0.0.

### Module format

[Section titled “Module format”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#module-format-1 "Copy link to this heading")

Node.js supports two distinct module formats with different capabilities and APIs: [ECMAScript modules](https://nodejs.org/api/esm.html) (or ES modules), an official standard format for JavaScript packages, and [CommonJS](https://nodejs.org/api/modules.html), a legacy format specific to Node.js.

The module format for each function will be determined by the file extension of its entry file:

- Functions with the `.mjs` extension are always executed as ES modules
- Functions with the `.cjs` extension are always executed as CommonJS
- Functions with the `.js` extension are executed as ES modules if the closest `package.json` file has a `type` property with the value `module`; otherwise they are executed as CommonJS

Choosing a module format has implications on how you write your function, especially when it comes to importing npm packages:

- CommonJS functions cannot use a static `import` to load npm packages written as ES modules and must use a [dynamic import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)
- ES modules functions cannot use named imports (for example, `import { kebabCase } from "lodash"`) when referencing npm packages written in CommonJS, and should instead use a default import (for example, `import _ from "lodash"`)
- In ES modules, Node.js built-in primitives like `__dirname` and `__filename` are not available and should be replaced with [`import.meta.url`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import.meta)

## Lambda compatibility

[Section titled “Lambda compatibility”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#lambda-compatibility-1 "Copy link to this heading")

Netlify Functions support an alternative API surface that is compatible with [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-nodejs.html). This may be useful if you’re looking to migrate Lambda workflows into Netlify with minimal refactoring required.

To opt-in, your handler function must be exported using a `handler` named export.

```
export const handler: Handler = async (event, context) => {

  return {

    body: JSON.stringify({ message: "Hello World" }),

    statusCode: 200

  };

};
```

For more information about this API, refer to [Lambda compatibility](https://docs.netlify.com/build/functions/lambda-compatibility).

## Test locally

[Section titled “Test locally”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#test-locally-1 "Copy link to this heading")

To streamline writing and testing your functions on Netlify, run a local development environment with [Netlify Dev](https://docs.netlify.com/api-and-cli-guides/cli-guides/local-development/). This feature of Netlify CLI includes tools for local function development through a simulated Netlify production environment. The `netlify dev` command starts a framework server if a framework is detected and handles redirects, proxy rules, environment variables, and Netlify Functions.

By default, the `geo` location used is the location of your local environment. To override this to a default mock location of San Francisco, CA, USA, use the `--geo=mock` flag. To mock a specific country, use `--geo=mock --country=` with a two-letter country code. For more information about the `--geo` flag, visit the [CLI docs](https://cli.netlify.com/commands/dev/).

## Next steps

[Section titled “Next steps”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#next-steps-1 "Copy link to this heading")

Push your function source files to your Git provider for continuous deployment where Netlify’s build system automatically detects, builds, and deploys your functions. For more control over the process, learn about [other workflows for deploying your functions](https://docs.netlify.com/build/functions/deploy/) including custom builds with continuous deployment and manual deploys with the Netlify CLI or API.

Monitor function [logs](https://docs.netlify.com/build/functions/logs/) and [metrics](https://docs.netlify.com/manage/monitoring/function-metrics/) in the Netlify UI to observe and help troubleshoot your deployed functions.

Netlify function logs are found in the Netlify UI. You can also stream Netlify function logs to the console with the [Netlify CLI](https://cli.netlify.com/commands/logs/#logsfunction).

## Use the Lambda-compatible API for Go

[Section titled “Use the Lambda-compatible API for Go”](https://docs.netlify.com/build/functions/get-started/?data-tab=TypeScript#use-the-lambda-compatible-api-for-go "Copy link to this heading")

To write functions in Go, use the [Lambda-compatible functions API](https://docs.netlify.com/build/functions/lambda-compatibility/?fn-language=go).

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
