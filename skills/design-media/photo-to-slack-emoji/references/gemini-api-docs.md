[Skip to main content](https://ai.google.dev/gemini-api/docs/image-generation#main-content)

[![Gemini API](https://ai.google.dev/_static/googledevai/images/gemini-api-logo.svg)](https://ai.google.dev/)

`/`

Language

- [English](https://ai.google.dev/gemini-api/docs/image-generation)
- [Deutsch](https://ai.google.dev/gemini-api/docs/image-generation?hl=de)
- [Español – América Latina](https://ai.google.dev/gemini-api/docs/image-generation?hl=es-419)
- [Français](https://ai.google.dev/gemini-api/docs/image-generation?hl=fr)
- [Indonesia](https://ai.google.dev/gemini-api/docs/image-generation?hl=id)
- [Italiano](https://ai.google.dev/gemini-api/docs/image-generation?hl=it)
- [Polski](https://ai.google.dev/gemini-api/docs/image-generation?hl=pl)
- [Português – Brasil](https://ai.google.dev/gemini-api/docs/image-generation?hl=pt-br)
- [Shqip](https://ai.google.dev/gemini-api/docs/image-generation?hl=sq)
- [Tiếng Việt](https://ai.google.dev/gemini-api/docs/image-generation?hl=vi)
- [Türkçe](https://ai.google.dev/gemini-api/docs/image-generation?hl=tr)
- [Русский](https://ai.google.dev/gemini-api/docs/image-generation?hl=ru)
- [עברית](https://ai.google.dev/gemini-api/docs/image-generation?hl=he)
- [العربيّة](https://ai.google.dev/gemini-api/docs/image-generation?hl=ar)
- [فارسی](https://ai.google.dev/gemini-api/docs/image-generation?hl=fa)
- [हिंदी](https://ai.google.dev/gemini-api/docs/image-generation?hl=hi)
- [বাংলা](https://ai.google.dev/gemini-api/docs/image-generation?hl=bn)
- [ภาษาไทย](https://ai.google.dev/gemini-api/docs/image-generation?hl=th)
- [中文 – 简体](https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn)
- [中文 – 繁體](https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-tw)
- [日本語](https://ai.google.dev/gemini-api/docs/image-generation?hl=ja)
- [한국어](https://ai.google.dev/gemini-api/docs/image-generation?hl=ko)

[Get API key](https://aistudio.google.com/apikey) [Cookbook](https://github.com/google-gemini/cookbook) [Community](https://discuss.ai.google.dev/c/gemini-api/)

[Sign in](https://ai.google.dev/_d/signin?continue=https%3A%2F%2Fai.google.dev%2Fgemini-api%2Fdocs%2Fimage-generation&prompt=select_account)

- On this page
- [Image generation (text-to-image)](https://ai.google.dev/gemini-api/docs/image-generation#image_generation_text-to-image)
- [Image editing (text-and-image-to-image)](https://ai.google.dev/gemini-api/docs/image-generation#gemini-image-editing)
- [Other image generation modes](https://ai.google.dev/gemini-api/docs/image-generation#other_image_generation_modes)
- [Prompting guide and strategies](https://ai.google.dev/gemini-api/docs/image-generation#prompt-guide)
  - [Prompts for generating images](https://ai.google.dev/gemini-api/docs/image-generation#image-generation-prompts)
  - [Prompts for editing images](https://ai.google.dev/gemini-api/docs/image-generation#image-editing-prompts)
  - [Best Practices](https://ai.google.dev/gemini-api/docs/image-generation#best-practices)
- [Limitations](https://ai.google.dev/gemini-api/docs/image-generation#limitations)
- [Optional configurations](https://ai.google.dev/gemini-api/docs/image-generation#optional_configurations)
  - [Output types](https://ai.google.dev/gemini-api/docs/image-generation#output_types)
  - [Aspect ratios](https://ai.google.dev/gemini-api/docs/image-generation#aspect_ratios)
- [When to use Imagen](https://ai.google.dev/gemini-api/docs/image-generation#choose-a-model)
- [What's next](https://ai.google.dev/gemini-api/docs/image-generation#what-is-next)

**Veo 3.1 is here!** Read about the new model and its features in the
[**blog post**](https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-controls-in-the-gemini-api/) and
[**documentation**](https://ai.google.dev/gemini-api/docs/video).


- [Home](https://ai.google.dev/)
- [Gemini API](https://ai.google.dev/gemini-api)
- [Gemini API docs](https://ai.google.dev/gemini-api/docs)

Was this helpful?



 Send feedback



# Image generation with Gemini (aka Nano Banana)    content\_copy

- On this page
- [Image generation (text-to-image)](https://ai.google.dev/gemini-api/docs/image-generation#image_generation_text-to-image)
- [Image editing (text-and-image-to-image)](https://ai.google.dev/gemini-api/docs/image-generation#gemini-image-editing)
- [Other image generation modes](https://ai.google.dev/gemini-api/docs/image-generation#other_image_generation_modes)
- [Prompting guide and strategies](https://ai.google.dev/gemini-api/docs/image-generation#prompt-guide)
  - [Prompts for generating images](https://ai.google.dev/gemini-api/docs/image-generation#image-generation-prompts)
  - [Prompts for editing images](https://ai.google.dev/gemini-api/docs/image-generation#image-editing-prompts)
  - [Best Practices](https://ai.google.dev/gemini-api/docs/image-generation#best-practices)
- [Limitations](https://ai.google.dev/gemini-api/docs/image-generation#limitations)
- [Optional configurations](https://ai.google.dev/gemini-api/docs/image-generation#optional_configurations)
  - [Output types](https://ai.google.dev/gemini-api/docs/image-generation#output_types)
  - [Aspect ratios](https://ai.google.dev/gemini-api/docs/image-generation#aspect_ratios)
- [When to use Imagen](https://ai.google.dev/gemini-api/docs/image-generation#choose-a-model)
- [What's next](https://ai.google.dev/gemini-api/docs/image-generation#what-is-next)

Gemini can generate and process images conversationally. You can prompt Gemini
with text, images, or a combination of both allowing you to create, edit, and
iterate on visuals with unprecedented control:

- **Text-to-Image:** Generate high-quality images from simple or complex text descriptions.
- **Image + Text-to-Image (Editing):** Provide an image and use text prompts to add, remove, or modify elements, change the style, or adjust the color grading.
- **Multi-Image to Image (Composition & Style Transfer):** Use multiple input images to compose a new scene or transfer the style from one image to another.
- **Iterative Refinement:** Engage in a conversation to progressively refine your image over multiple turns, making small adjustments until it's perfect.
- **High-Fidelity Text Rendering:** Accurately generate images that contain legible and well-placed text, ideal for logos, diagrams, and posters.

All generated images include a [SynthID watermark](https://ai.google.dev/responsible/docs/safeguards/synthid).

## Image generation (text-to-image)

The following code demonstrates how to generate an image based on a descriptive
prompt.

[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

prompt = (
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt],
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("generated_image.png")

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("gemini-native-image.png", buffer);
      console.log("Image saved as gemini-native-image.png");
    }
  }
}

main();

```

```
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {

  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-2.5-flash-image",
      genai.Text("Create a picture of a nano banana dish in a " +
                 " fancy restaurant with a Gemini theme"),
  )

  for _, part := range result.Candidates[0].Content.Parts {
      if part.Text != "" {
          fmt.Println(part.Text)
      } else if part.InlineData != nil {
          imageBytes := part.InlineData.Data
          outputFilename := "gemini_generated_image.png"
          _ = os.WriteFile(outputFilename, imageBytes, 0644)
      }
  }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > gemini-native-image.png

```

![AI-generated image of a nano banana dish](https://ai.google.dev/static/gemini-api/docs/images/nano-banana.png)AI-generated image of a nano banana dish in a Gemini-themed restaurant

## Image editing (text-and-image-to-image)

**Reminder**: Make sure you have the necessary rights to any images you upload.
Don't generate content that infringe on others' rights, including videos or
images that deceive, harass, or harm. Your use of this generative AI service is
subject to our [Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy).

The following example demonstrates uploading base64 encoded images.
For multiple images, larger payloads, and supported MIME types, check the [Image\\
understanding](https://ai.google.dev/gemini-api/docs/image-understanding) page.

[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

prompt = (
    "Create a picture of my cat eating a nano-banana in a "
    "fancy restaurant under the Gemini constellation",
)

image = Image.open("/path/to/cat_image.png")

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, image],
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("generated_image.png")

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const imagePath = "path/to/cat_image.png";
  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString("base64");

  const prompt = [\
    { text: "Create a picture of my cat eating a nano-banana in a" +\
            "fancy restaurant under the Gemini constellation" },\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image,\
      },\
    },\
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("gemini-native-image.png", buffer);
      console.log("Image saved as gemini-native-image.png");
    }
  }
}

main();

```

```
package main

import (
 "context"
 "fmt"
 "os"
 "google.golang.org/genai"
)

func main() {

 ctx := context.Background()
 client, err := genai.NewClient(ctx, nil)
 if err != nil {
     log.Fatal(err)
 }

 imagePath := "/path/to/cat_image.png"
 imgData, _ := os.ReadFile(imagePath)

 parts := []*genai.Part{
   genai.NewPartFromText("Create a picture of my cat eating a nano-banana in a fancy restaurant under the Gemini constellation"),
   &genai.Part{
     InlineData: &genai.Blob{
       MIMEType: "image/png",
       Data:     imgData,
     },
   },
 }

 contents := []*genai.Content{
   genai.NewContentFromParts(parts, genai.RoleUser),
 }

 result, _ := client.Models.GenerateContent(
     ctx,
     "gemini-2.5-flash-image",
     contents,
 )

 for _, part := range result.Candidates[0].Content.Parts {
     if part.Text != "" {
         fmt.Println(part.Text)
     } else if part.InlineData != nil {
         imageBytes := part.InlineData.Data
         outputFilename := "gemini_generated_image.png"
         _ = os.WriteFile(outputFilename, imageBytes, 0644)
     }
 }
}

```

```
IMG_PATH=/path/to/cat_image.jpeg

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

IMG_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH" 2>&1)

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "{
      \"contents\": [{\
        \"parts\":[\
            {\"text\": \"'Create a picture of my cat eating a nano-banana in a fancy restaurant under the Gemini constellation\"},\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/jpeg\",\
                \"data\": \"$IMG_BASE64\"\
              }\
            }\
        ]\
      }]
    }"  \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > gemini-edited-image.png

```

![AI-generated image of a cat eating anano banana](https://ai.google.dev/static/gemini-api/docs/images/cat-banana.png)AI-generated image of a cat eating a nano banana

## Other image generation modes

Gemini supports other image interaction modes based on prompt structure and
context, including:

- **Text to image(s) and text (interleaved):** Outputs images with related text.

  - Example prompt: "Generate an illustrated recipe for a paella."
- **Image(s) and text to image(s) and text (interleaved)**: Uses input images and text to create new related images and text.

  - Example prompt: (With an image of a furnished room) "What other color sofas would work in my space? can you update the image?"
- **Multi-turn image editing (chat):** Keep generating and editing images conversationally.

  - Example prompts: \[upload an image of a blue car.\] , "Turn this car into a convertible.", "Now change the color to yellow."

## Prompting guide and strategies

Mastering Gemini 2.5 Flash Image Generation starts with one fundamental
principle:

> **Describe the scene, don't just list keywords.**
> The model's core strength is its deep language understanding. A narrative,
> descriptive paragraph will almost always produce a better, more coherent image
> than a list of disconnected words.

### Prompts for generating images

The following strategies will help you create effective prompts to
generate exactly the images you're looking for.

#### 1. Photorealistic scenes

For realistic images, use photography terms. Mention camera angles, lens types,
lighting, and fine details to guide the model toward a photorealistic result.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
A photorealistic [shot type] of [subject], [action or expression], set in
[environment]. The scene is illuminated by [lighting description], creating
a [mood] atmosphere. Captured with a [camera/lens details], emphasizing
[key textures and details]. The image should be in a [aspect ratio] format.

```

```
A photorealistic close-up portrait of an elderly Japanese ceramicist with
deep, sun-etched wrinkles and a warm, knowing smile. He is carefully
inspecting a freshly glazed tea bowl. The setting is his rustic,
sun-drenched workshop. The scene is illuminated by soft, golden hour light
streaming through a window, highlighting the fine texture of the clay.
Captured with an 85mm portrait lens, resulting in a soft, blurred background
(bokeh). The overall mood is serene and masterful. Vertical portrait
orientation.

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A photorealistic close-up portrait of an elderly Japanese ceramicist with deep, sun-etched wrinkles and a warm, knowing smile. He is carefully inspecting a freshly glazed tea bowl. The setting is his rustic, sun-drenched workshop with pottery wheels and shelves of clay pots in the background. The scene is illuminated by soft, golden hour light streaming through a window, highlighting the fine texture of the clay and the fabric of his apron. Captured with an 85mm portrait lens, resulting in a soft, blurred background (bokeh). The overall mood is serene and masterful.",
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('photorealistic_example.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "A photorealistic close-up portrait of an elderly Japanese ceramicist with deep, sun-etched wrinkles and a warm, knowing smile. He is carefully inspecting a freshly glazed tea bowl. The setting is his rustic, sun-drenched workshop with pottery wheels and shelves of clay pots in the background. The scene is illuminated by soft, golden hour light streaming through a window, highlighting the fine texture of the clay and the fabric of his apron. Captured with an 85mm portrait lens, resulting in a soft, blurred background (bokeh). The overall mood is serene and masterful.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("photorealistic_example.png", buffer);
      console.log("Image saved as photorealistic_example.png");
    }
  }
}

main();

```

```
package main

import (
    "context"
    "fmt"
    "os"
    "google.golang.org/genai"
)

func main() {

    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash-image",
        genai.Text("A photorealistic close-up portrait of an elderly Japanese ceramicist with deep, sun-etched wrinkles and a warm, knowing smile. He is carefully inspecting a freshly glazed tea bowl. The setting is his rustic, sun-drenched workshop with pottery wheels and shelves of clay pots in the background. The scene is illuminated by soft, golden hour light streaming through a window, highlighting the fine texture of the clay and the fabric of his apron. Captured with an 85mm portrait lens, resulting in a soft, blurred background (bokeh). The overall mood is serene and masterful."),
    )

    for _, part := range result.Candidates[0].Content.Parts {
        if part.Text != "" {
            fmt.Println(part.Text)
        } else if part.InlineData != nil {
            imageBytes := part.InlineData.Data
            outputFilename := "photorealistic_example.png"
            _ = os.WriteFile(outputFilename, imageBytes, 0644)
        }
    }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "A photorealistic close-up portrait of an elderly Japanese ceramicist with deep, sun-etched wrinkles and a warm, knowing smile. He is carefully inspecting a freshly glazed tea bowl. The setting is his rustic, sun-drenched workshop with pottery wheels and shelves of clay pots in the background. The scene is illuminated by soft, golden hour light streaming through a window, highlighting the fine texture of the clay and the fabric of his apron. Captured with an 85mm portrait lens, resulting in a soft, blurred background (bokeh). The overall mood is serene and masterful."}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > photorealistic_example.png

```

![A photorealistic close-up portrait of an elderly Japanese ceramicist...](https://ai.google.dev/static/gemini-api/docs/images/photorealistic_example.png)A photorealistic close-up portrait of an elderly Japanese ceramicist...

#### 2. Stylized illustrations & stickers

To create stickers, icons, or assets, be explicit about the style and request a
transparent background.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
A [style] sticker of a [subject], featuring [key characteristics] and a
[color palette]. The design should have [line style] and [shading style].
The background must be transparent.

```

```
A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's
munching on a green bamboo leaf. The design features bold, clean outlines,
simple cel-shading, and a vibrant color palette. The background must be white.

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's munching on a green bamboo leaf. The design features bold, clean outlines, simple cel-shading, and a vibrant color palette. The background must be white.",
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('red_panda_sticker.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's munching on a green bamboo leaf. The design features bold, clean outlines, simple cel-shading, and a vibrant color palette. The background must be white.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("red_panda_sticker.png", buffer);
      console.log("Image saved as red_panda_sticker.png");
    }
  }
}

main();

```

```
package main

import (
    "context"
    "fmt"
    "os"
    "google.golang.org/genai"
)

func main() {

    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash-image",
        genai.Text("A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's munching on a green bamboo leaf. The design features bold, clean outlines, simple cel-shading, and a vibrant color palette. The background must be white."),
    )

    for _, part := range result.Candidates[0].Content.Parts {
        if part.Text != "" {
            fmt.Println(part.Text)
        } else if part.InlineData != nil {
            imageBytes := part.InlineData.Data
            outputFilename := "red_panda_sticker.png"
            _ = os.WriteFile(outputFilename, imageBytes, 0644)
        }
    }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It'"'"'s munching on a green bamboo leaf. The design features bold, clean outlines, simple cel-shading, and a vibrant color palette. The background must be white."}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > red_panda_sticker.png

```

![A kawaii-style sticker of a happy red...](https://ai.google.dev/static/gemini-api/docs/images/red_panda_sticker.png)A kawaii-style sticker of a happy red panda...

#### 3. Accurate text in images

Gemini excels at rendering text. Be clear about the text, the font style
(descriptively), and the overall design.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
Create a [image type] for [brand/concept] with the text "[text to render]"
in a [font style]. The design should be [style description], with a
[color scheme].

```

```
Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'.
The text should be in a clean, bold, sans-serif font. The design should
feature a simple, stylized icon of a a coffee bean seamlessly integrated
with the text. The color scheme is black and white.

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'. The text should be in a clean, bold, sans-serif font. The design should feature a simple, stylized icon of a a coffee bean seamlessly integrated with the text. The color scheme is black and white.",
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('logo_example.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'. The text should be in a clean, bold, sans-serif font. The design should feature a simple, stylized icon of a a coffee bean seamlessly integrated with the text. The color scheme is black and white.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("logo_example.png", buffer);
      console.log("Image saved as logo_example.png");
    }
  }
}

main();

```

```
package main

import (
    "context"
    "fmt"
    "os"
    "google.golang.org/genai"
)

func main() {

    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash-image",
        genai.Text("Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'. The text should be in a clean, bold, sans-serif font. The design should feature a simple, stylized icon of a a coffee bean seamlessly integrated with the text. The color scheme is black and white."),
    )

    for _, part := range result.Candidates[0].Content.Parts {
        if part.Text != "" {
            fmt.Println(part.Text)
        } else if part.InlineData != nil {
            imageBytes := part.InlineData.Data
            outputFilename := "logo_example.png"
            _ = os.WriteFile(outputFilename, imageBytes, 0644)
        }
    }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "Create a modern, minimalist logo for a coffee shop called '"'"'The Daily Grind'"'"'. The text should be in a clean, bold, sans-serif font. The design should feature a simple, stylized icon of a a coffee bean seamlessly integrated with the text. The color scheme is black and white."}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > logo_example.png

```

![Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'...](https://ai.google.dev/static/gemini-api/docs/images/logo_example.png)Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'...

#### 4. Product mockups & commercial photography

Perfect for creating clean, professional product shots for e-commerce,
advertising, or branding.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
A high-resolution, studio-lit product photograph of a [product description]
on a [background surface/description]. The lighting is a [lighting setup,\
e.g., three-point softbox setup] to [lighting purpose]. The camera angle is
a [angle type] to showcase [specific feature]. Ultra-realistic, with sharp
focus on [key detail]. [Aspect ratio].

```

```
A high-resolution, studio-lit product photograph of a minimalist ceramic
coffee mug in matte black, presented on a polished concrete surface. The
lighting is a three-point softbox setup designed to create soft, diffused
highlights and eliminate harsh shadows. The camera angle is a slightly
elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with
sharp focus on the steam rising from the coffee. Square image.

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug in matte black, presented on a polished concrete surface. The lighting is a three-point softbox setup designed to create soft, diffused highlights and eliminate harsh shadows. The camera angle is a slightly elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with sharp focus on the steam rising from the coffee. Square image.",
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('product_mockup.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug in matte black, presented on a polished concrete surface. The lighting is a three-point softbox setup designed to create soft, diffused highlights and eliminate harsh shadows. The camera angle is a slightly elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with sharp focus on the steam rising from the coffee. Square image.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("product_mockup.png", buffer);
      console.log("Image saved as product_mockup.png");
    }
  }
}

main();

```

```
package main

import (
    "context"
    "fmt"
    "os"
    "google.golang.org/genai"
)

func main() {

    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash-image",
        genai.Text("A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug in matte black, presented on a polished concrete surface. The lighting is a three-point softbox setup designed to create soft, diffused highlights and eliminate harsh shadows. The camera angle is a slightly elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with sharp focus on the steam rising from the coffee. Square image."),
    )

    for _, part := range result.Candidates[0].Content.Parts {
        if part.Text != "" {
            fmt.Println(part.Text)
        } else if part.InlineData != nil {
            imageBytes := part.InlineData.Data
            outputFilename := "product_mockup.png"
            _ = os.WriteFile(outputFilename, imageBytes, 0644)
        }
    }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug in matte black, presented on a polished concrete surface. The lighting is a three-point softbox setup designed to create soft, diffused highlights and eliminate harsh shadows. The camera angle is a slightly elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with sharp focus on the steam rising from the coffee. Square image."}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > product_mockup.png

```

![A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug...](https://ai.google.dev/static/gemini-api/docs/images/product_mockup.png)A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug...

#### 5. Minimalist & negative space design

Excellent for creating backgrounds for websites, presentations, or marketing
materials where text will be overlaid.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
A minimalist composition featuring a single [subject] positioned in the
[bottom-right/top-left/etc.] of the frame. The background is a vast, empty
[color] canvas, creating significant negative space. Soft, subtle lighting.
[Aspect ratio].

```

```
A minimalist composition featuring a single, delicate red maple leaf
positioned in the bottom-right of the frame. The background is a vast, empty
off-white canvas, creating significant negative space for text. Soft,
diffused lighting from the top left. Square image.

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A minimalist composition featuring a single, delicate red maple leaf positioned in the bottom-right of the frame. The background is a vast, empty off-white canvas, creating significant negative space for text. Soft, diffused lighting from the top left. Square image.",
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('minimalist_design.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "A minimalist composition featuring a single, delicate red maple leaf positioned in the bottom-right of the frame. The background is a vast, empty off-white canvas, creating significant negative space for text. Soft, diffused lighting from the top left. Square image.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("minimalist_design.png", buffer);
      console.log("Image saved as minimalist_design.png");
    }
  }
}

main();

```

```
package main

import (
    "context"
    "fmt"
    "os"
    "google.golang.org/genai"
)

func main() {

    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash-image",
        genai.Text("A minimalist composition featuring a single, delicate red maple leaf positioned in the bottom-right of the frame. The background is a vast, empty off-white canvas, creating significant negative space for text. Soft, diffused lighting from the top left. Square image."),
    )

    for _, part := range result.Candidates[0].Content.Parts {
        if part.Text != "" {
            fmt.Println(part.Text)
        } else if part.InlineData != nil {
            imageBytes := part.InlineData.Data
            outputFilename := "minimalist_design.png"
            _ = os.WriteFile(outputFilename, imageBytes, 0644)
        }
    }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "A minimalist composition featuring a single, delicate red maple leaf positioned in the bottom-right of the frame. The background is a vast, empty off-white canvas, creating significant negative space for text. Soft, diffused lighting from the top left. Square image."}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > minimalist_design.png

```

![A minimalist composition featuring a single, delicate red maple leaf...](https://ai.google.dev/static/gemini-api/docs/images/minimalist_design.png)A minimalist composition featuring a single, delicate red maple leaf...

#### 6. Sequential art (Comic panel / Storyboard)

Builds on character consistency and scene description to create panels for
visual storytelling.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
A single comic book panel in a [art style] style. In the foreground,
[character description and action]. In the background, [setting details].
The panel has a [dialogue/caption box] with the text "[Text]". The lighting
creates a [mood] mood. [Aspect ratio].

```

```
A single comic book panel in a gritty, noir art style with high-contrast
black and white inks. In the foreground, a detective in a trench coat stands
under a flickering streetlamp, rain soaking his shoulders. In the
background, the neon sign of a desolate bar reflects in a puddle. A caption
box at the top reads "The city was a tough place to keep secrets." The
lighting is harsh, creating a dramatic, somber mood. Landscape.

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A single comic book panel in a gritty, noir art style with high-contrast black and white inks. In the foreground, a detective in a trench coat stands under a flickering streetlamp, rain soaking his shoulders. In the background, the neon sign of a desolate bar reflects in a puddle. A caption box at the top reads \"The city was a tough place to keep secrets.\" The lighting is harsh, creating a dramatic, somber mood. Landscape.",
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('comic_panel.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const prompt =
    "A single comic book panel in a gritty, noir art style with high-contrast black and white inks. In the foreground, a detective in a trench coat stands under a flickering streetlamp, rain soaking his shoulders. In the background, the neon sign of a desolate bar reflects in a puddle. A caption box at the top reads \"The city was a tough place to keep secrets.\" The lighting is harsh, creating a dramatic, somber mood. Landscape.";

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("comic_panel.png", buffer);
      console.log("Image saved as comic_panel.png");
    }
  }
}

main();

```

```
package main

import (
    "context"
    "fmt"
    "os"
    "google.golang.org/genai"
)

func main() {

    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash-image",
        genai.Text("A single comic book panel in a gritty, noir art style with high-contrast black and white inks. In the foreground, a detective in a trench coat stands under a flickering streetlamp, rain soaking his shoulders. In the background, the neon sign of a desolate bar reflects in a puddle. A caption box at the top reads \"The city was a tough place to keep secrets.\" The lighting is harsh, creating a dramatic, somber mood. Landscape."),
    )

    for _, part := range result.Candidates[0].Content.Parts {
        if part.Text != "" {
            fmt.Println(part.Text)
        } else if part.InlineData != nil {
            imageBytes := part.InlineData.Data
            outputFilename := "comic_panel.png"
            _ = os.WriteFile(outputFilename, imageBytes, 0644)
        }
    }
}

```

```
curl -s -X POST
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{\
      "parts": [\
        {"text": "A single comic book panel in a gritty, noir art style with high-contrast black and white inks. In the foreground, a detective in a trench coat stands under a flickering streetlamp, rain soaking his shoulders. In the background, the neon sign of a desolate bar reflects in a puddle. A caption box at the top reads \"The city was a tough place to keep secrets.\" The lighting is harsh, creating a dramatic, somber mood. Landscape."}\
      ]\
    }]
  }' \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > comic_panel.png

```

![A single comic book panel in a gritty, noir art style...](https://ai.google.dev/static/gemini-api/docs/images/comic_panel.png)A single comic book panel in a gritty, noir art style...

### Prompts for editing images

These examples show how to provide images alongside your text prompts for
editing, composition, and style transfer.

#### 1. Adding and removing elements

Provide an image and describe your change. The model will match the original
image's style, lighting, and perspective.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
Using the provided image of [subject], please [add/remove/modify] [element]
to/from the scene. Ensure the change is [description of how the change should\
integrate].

```

```
"Using the provided image of my cat, please add a small, knitted wizard hat
on its head. Make it look like it's sitting comfortably and matches the soft
lighting of the photo."

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Base image prompt: "A photorealistic picture of a fluffy ginger cat sitting on a wooden floor, looking directly at the camera. Soft, natural light from a window."
image_input = Image.open('/path/to/your/cat_photo.png')
text_input = """Using the provided image of my cat, please add a small, knitted wizard hat on its head. Make it look like it's sitting comfortably and not falling off."""

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[text_input, image_input],
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('cat_with_hat.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const imagePath = "/path/to/your/cat_photo.png";
  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString("base64");

  const prompt = [\
    { text: "Using the provided image of my cat, please add a small, knitted wizard hat on its head. Make it look like it's sitting comfortably and not falling off." },\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image,\
      },\
    },\
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("cat_with_hat.png", buffer);
      console.log("Image saved as cat_with_hat.png");
    }
  }
}

main();

```

```
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {

  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  imagePath := "/path/to/your/cat_photo.png"
  imgData, _ := os.ReadFile(imagePath)

  parts := []*genai.Part{
    genai.NewPartFromText("Using the provided image of my cat, please add a small, knitted wizard hat on its head. Make it look like it's sitting comfortably and not falling off."),
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData,
      },
    },
  }

  contents := []*genai.Content{
    genai.NewContentFromParts(parts, genai.RoleUser),
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-2.5-flash-image",
      contents,
  )

  for _, part := range result.Candidates[0].Content.Parts {
      if part.Text != "" {
          fmt.Println(part.Text)
      } else if part.InlineData != nil {
          imageBytes := part.InlineData.Data
          outputFilename := "cat_with_hat.png"
          _ = os.WriteFile(outputFilename, imageBytes, 0644)
      }
  }
}

```

```
IMG_PATH=/path/to/your/cat_photo.png

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

IMG_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH" 2>&1)

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "{
      \"contents\": [{\
        \"parts\":[\
            {\"text\": \"Using the provided image of my cat, please add a small, knitted wizard hat on its head. Make it look like it's sitting comfortably and not falling off.\"},\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG_BASE64\"\
              }\
            }\
        ]\
      }]
    }"  \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > cat_with_hat.png

```

|     |     |
| --- | --- |
| Input | Output |
| ![A photorealistic picture of a fluffy ginger cat..](https://ai.google.dev/static/gemini-api/docs/images/cat.png)A photorealistic picture of a fluffy ginger cat... | ![Using the provided image of my cat, please add a small, knitted wizard hat...](https://ai.google.dev/static/gemini-api/docs/images/cat_with_hat.png)Using the provided image of my cat, please add a small, knitted wizard hat... |

#### 2. Inpainting (Semantic masking)

Conversationally define a "mask" to edit a specific part of an image while
leaving the rest untouched.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
Using the provided image, change only the [specific element] to [new\
element/description]. Keep everything else in the image exactly the same,
preserving the original style, lighting, and composition.

```

```
"Using the provided image of a living room, change only the blue sofa to be
a vintage, brown leather chesterfield sofa. Keep the rest of the room,
including the pillows on the sofa and the lighting, unchanged."

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Base image prompt: "A wide shot of a modern, well-lit living room with a prominent blue sofa in the center. A coffee table is in front of it and a large window is in the background."
living_room_image = Image.open('/path/to/your/living_room.png')
text_input = """Using the provided image of a living room, change only the blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest of the room, including the pillows on the sofa and the lighting, unchanged."""

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[living_room_image, text_input],
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('living_room_edited.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const imagePath = "/path/to/your/living_room.png";
  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString("base64");

  const prompt = [\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image,\
      },\
    },\
    { text: "Using the provided image of a living room, change only the blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest of the room, including the pillows on the sofa and the lighting, unchanged." },\
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("living_room_edited.png", buffer);
      console.log("Image saved as living_room_edited.png");
    }
  }
}

main();

```

```
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {

  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  imagePath := "/path/to/your/living_room.png"
  imgData, _ := os.ReadFile(imagePath)

  parts := []*genai.Part{
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData,
      },
    },
    genai.NewPartFromText("Using the provided image of a living room, change only the blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest of the room, including the pillows on the sofa and the lighting, unchanged."),
  }

  contents := []*genai.Content{
    genai.NewContentFromParts(parts, genai.RoleUser),
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-2.5-flash-image",
      contents,
  )

  for _, part := range result.Candidates[0].Content.Parts {
      if part.Text != "" {
          fmt.Println(part.Text)
      } else if part.InlineData != nil {
          imageBytes := part.InlineData.Data
          outputFilename := "living_room_edited.png"
          _ = os.WriteFile(outputFilename, imageBytes, 0644)
      }
  }
}

```

```
IMG_PATH=/path/to/your/living_room.png

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

IMG_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH" 2>&1)

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "{
      \"contents\": [{\
        \"parts\":[\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG_BASE64\"\
              }\
            },\
            {\"text\": \"Using the provided image of a living room, change only the blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest of the room, including the pillows on the sofa and the lighting, unchanged.\"}\
        ]\
      }]
    }"  \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > living_room_edited.png

```

|     |     |
| --- | --- |
| Input | Output |
| ![A wide shot of a modern, well-lit living room...](https://ai.google.dev/static/gemini-api/docs/images/living_room.png)A wide shot of a modern, well-lit living room... | ![Using the provided image of a living room, change only the blue sofa to be a vintage, brown leather chesterfield sofa...](https://ai.google.dev/static/gemini-api/docs/images/living_room_edited.png)Using the provided image of a living room, change only the blue sofa to be a vintage, brown leather chesterfield sofa... |

#### 3. Style transfer

Provide an image and ask the model to recreate its content in a different
artistic style.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
Transform the provided photograph of [subject] into the artistic style of [artist/art style]. Preserve the original composition but render it with [description of stylistic elements].

```

```
"Transform the provided photograph of a modern city street at night into the artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original composition of buildings and cars, but render all elements with swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows."

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Base image prompt: "A photorealistic, high-resolution photograph of a busy city street in New York at night, with bright neon signs, yellow taxis, and tall skyscrapers."
city_image = Image.open('/path/to/your/city.png')
text_input = """Transform the provided photograph of a modern city street at night into the artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original composition of buildings and cars, but render all elements with swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows."""

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[city_image, text_input],
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('city_style_transfer.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const imagePath = "/path/to/your/city.png";
  const imageData = fs.readFileSync(imagePath);
  const base64Image = imageData.toString("base64");

  const prompt = [\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image,\
      },\
    },\
    { text: "Transform the provided photograph of a modern city street at night into the artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original composition of buildings and cars, but render all elements with swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows." },\
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("city_style_transfer.png", buffer);
      console.log("Image saved as city_style_transfer.png");
    }
  }
}

main();

```

```
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {

  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  imagePath := "/path/to/your/city.png"
  imgData, _ := os.ReadFile(imagePath)

  parts := []*genai.Part{
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData,
      },
    },
    genai.NewPartFromText("Transform the provided photograph of a modern city street at night into the artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original composition of buildings and cars, but render all elements with swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows."),
  }

  contents := []*genai.Content{
    genai.NewContentFromParts(parts, genai.RoleUser),
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-2.5-flash-image",
      contents,
  )

  for _, part := range result.Candidates[0].Content.Parts {
      if part.Text != "" {
          fmt.Println(part.Text)
      } else if part.InlineData != nil {
          imageBytes := part.InlineData.Data
          outputFilename := "city_style_transfer.png"
          _ = os.WriteFile(outputFilename, imageBytes, 0644)
      }
  }
}

```

```
IMG_PATH=/path/to/your/city.png

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

IMG_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH" 2>&1)

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "{
      \"contents\": [{\
        \"parts\":[\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG_BASE64\"\
              }\
            },\
            {\"text\": \"Transform the provided photograph of a modern city street at night into the artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original composition of buildings and cars, but render all elements with swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows.\"}\
        ]\
      }]
    }"  \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > city_style_transfer.png

```

|     |     |
| --- | --- |
| Input | Output |
| ![A photorealistic, high-resolution photograph of a busy city street...](https://ai.google.dev/static/gemini-api/docs/images/city.png)A photorealistic, high-resolution photograph of a busy city street... | ![Transform the provided photograph of a modern city street at night...](https://ai.google.dev/static/gemini-api/docs/images/city_style_transfer.png)Transform the provided photograph of a modern city street at night... |

#### 4. Advanced composition: Combining multiple images

Provide multiple images as context to create a new, composite scene. This is
perfect for product mockups or creative collages.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
Create a new image by combining the elements from the provided images. Take
the [element from image 1] and place it with/on the [element from image 2].
The final image should be a [description of the final scene].

```

```
"Create a professional e-commerce fashion photo. Take the blue floral dress
from the first image and let the woman from the second image wear it.
Generate a realistic, full-body shot of the woman wearing the dress, with
the lighting and shadows adjusted to match the outdoor environment."

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Base image prompts:
# 1. Dress: "A professionally shot photo of a blue floral summer dress on a plain white background, ghost mannequin style."
# 2. Model: "Full-body shot of a woman with her hair in a bun, smiling, standing against a neutral grey studio background."
dress_image = Image.open('/path/to/your/dress.png')
model_image = Image.open('/path/to/your/model.png')

text_input = """Create a professional e-commerce fashion photo. Take the blue floral dress from the first image and let the woman from the second image wear it. Generate a realistic, full-body shot of the woman wearing the dress, with the lighting and shadows adjusted to match the outdoor environment."""

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[dress_image, model_image, text_input],
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('fashion_ecommerce_shot.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const imagePath1 = "/path/to/your/dress.png";
  const imageData1 = fs.readFileSync(imagePath1);
  const base64Image1 = imageData1.toString("base64");
  const imagePath2 = "/path/to/your/model.png";
  const imageData2 = fs.readFileSync(imagePath2);
  const base64Image2 = imageData2.toString("base64");

  const prompt = [\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image1,\
      },\
    },\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image2,\
      },\
    },\
    { text: "Create a professional e-commerce fashion photo. Take the blue floral dress from the first image and let the woman from the second image wear it. Generate a realistic, full-body shot of the woman wearing the dress, with the lighting and shadows adjusted to match the outdoor environment." },\
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("fashion_ecommerce_shot.png", buffer);
      console.log("Image saved as fashion_ecommerce_shot.png");
    }
  }
}

main();

```

```
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {

  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  imgData1, _ := os.ReadFile("/path/to/your/dress.png")
  imgData2, _ := os.ReadFile("/path/to/your/model.png")

  parts := []*genai.Part{
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData1,
      },
    },
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData2,
      },
    },
    genai.NewPartFromText("Create a professional e-commerce fashion photo. Take the blue floral dress from the first image and let the woman from the second image wear it. Generate a realistic, full-body shot of the woman wearing the dress, with the lighting and shadows adjusted to match the outdoor environment."),
  }

  contents := []*genai.Content{
    genai.NewContentFromParts(parts, genai.RoleUser),
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-2.5-flash-image",
      contents,
  )

  for _, part := range result.Candidates[0].Content.Parts {
      if part.Text != "" {
          fmt.Println(part.Text)
      } else if part.InlineData != nil {
          imageBytes := part.InlineData.Data
          outputFilename := "fashion_ecommerce_shot.png"
          _ = os.WriteFile(outputFilename, imageBytes, 0644)
      }
  }
}

```

```
IMG_PATH1=/path/to/your/dress.png
IMG_PATH2=/path/to/your/model.png

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

IMG1_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH1" 2>&1)
IMG2_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH2" 2>&1)

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "{
      \"contents\": [{\
        \"parts\":[\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG1_BASE64\"\
              }\
            },\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG2_BASE64\"\
              }\
            },\
            {\"text\": \"Create a professional e-commerce fashion photo. Take the blue floral dress from the first image and let the woman from the second image wear it. Generate a realistic, full-body shot of the woman wearing the dress, with the lighting and shadows adjusted to match the outdoor environment.\"}\
        ]\
      }]
    }"  \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > fashion_ecommerce_shot.png

```

|     |     |     |
| --- | --- | --- |
| Input 1 | Input 2 | Output |
| ![A professionally shot photo of a blue floral summer dress...](https://ai.google.dev/static/gemini-api/docs/images/dress.png)A professionally shot photo of a blue floral summer dress... | ![Full-body shot of a woman with her hair in a bun...](https://ai.google.dev/static/gemini-api/docs/images/model.png)Full-body shot of a woman with her hair in a bun... | ![Create a professional e-commerce fashion photo...](https://ai.google.dev/static/gemini-api/docs/images/fashion_ecommerce_shot.png)Create a professional e-commerce fashion photo... |

#### 5. High-fidelity detail preservation

To ensure critical details (like a face or logo) are preserved during an edit,
describe them in great detail along with your edit request.

[Template](https://ai.google.dev/gemini-api/docs/image-generation#template)[Prompt](https://ai.google.dev/gemini-api/docs/image-generation#prompt)[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
Using the provided images, place [element from image 2] onto [element from\
image 1]. Ensure that the features of [element from image 1] remain
completely unchanged. The added element should [description of how the\
element should integrate].

```

```
"Take the first image of the woman with brown hair, blue eyes, and a neutral
expression. Add the logo from the second image onto her black t-shirt.
Ensure the woman's face and features remain completely unchanged. The logo
should look like it's naturally printed on the fabric, following the folds
of the shirt."

```

```
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

# Base image prompts:
# 1. Woman: "A professional headshot of a woman with brown hair and blue eyes, wearing a plain black t-shirt, against a neutral studio background."
# 2. Logo: "A simple, modern logo with the letters 'G' and 'A' in a white circle."
woman_image = Image.open('/path/to/your/woman.png')
logo_image = Image.open('/path/to/your/logo.png')
text_input = """Take the first image of the woman with brown hair, blue eyes, and a neutral expression. Add the logo from the second image onto her black t-shirt. Ensure the woman's face and features remain completely unchanged. The logo should look like it's naturally printed on the fabric, following the folds of the shirt."""

# Generate an image from a text prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[woman_image, logo_image, text_input],
)

image_parts = [\
    part.inline_data.data\
    for part in response.candidates[0].content.parts\
    if part.inline_data\
]

if image_parts:
    image = Image.open(BytesIO(image_parts[0]))
    image.save('woman_with_logo.png')
    image.show()

```

```
import { GoogleGenAI, Modality } from "@google/genai";
import * as fs from "node:fs";

async function main() {

  const ai = new GoogleGenAI({});

  const imagePath1 = "/path/to/your/woman.png";
  const imageData1 = fs.readFileSync(imagePath1);
  const base64Image1 = imageData1.toString("base64");
  const imagePath2 = "/path/to/your/logo.png";
  const imageData2 = fs.readFileSync(imagePath2);
  const base64Image2 = imageData2.toString("base64");

  const prompt = [\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image1,\
      },\
    },\
    {\
      inlineData: {\
        mimeType: "image/png",\
        data: base64Image2,\
      },\
    },\
    { text: "Take the first image of the woman with brown hair, blue eyes, and a neutral expression. Add the logo from the second image onto her black t-shirt. Ensure the woman's face and features remain completely unchanged. The logo should look like it's naturally printed on the fabric, following the folds of the shirt." },\
  ];

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
  });
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("woman_with_logo.png", buffer);
      console.log("Image saved as woman_with_logo.png");
    }
  }
}

main();

```

```
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {

  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  imgData1, _ := os.ReadFile("/path/to/your/woman.png")
  imgData2, _ := os.ReadFile("/path/to/your/logo.png")

  parts := []*genai.Part{
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData1,
      },
    },
    &genai.Part{
      InlineData: &genai.Blob{
        MIMEType: "image/png",
        Data:     imgData2,
      },
    },
    genai.NewPartFromText("Take the first image of the woman with brown hair, blue eyes, and a neutral expression. Add the logo from the second image onto her black t-shirt. Ensure the woman's face and features remain completely unchanged. The logo should look like it's naturally printed on the fabric, following the folds of the shirt."),
  }

  contents := []*genai.Content{
    genai.NewContentFromParts(parts, genai.RoleUser),
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-2.5-flash-image",
      contents,
  )

  for _, part := range result.Candidates[0].Content.Parts {
      if part.Text != "" {
          fmt.Println(part.Text)
      } else if part.InlineData != nil {
          imageBytes := part.InlineData.Data
          outputFilename := "woman_with_logo.png"
          _ = os.WriteFile(outputFilename, imageBytes, 0644)
      }
  }
}

```

```
IMG_PATH1=/path/to/your/woman.png
IMG_PATH2=/path/to/your/logo.png

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

IMG1_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH1" 2>&1)
IMG2_BASE64=$(base64 "$B64FLAGS" "$IMG_PATH2" 2>&1)

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "{
      \"contents\": [{\
        \"parts\":[\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG1_BASE64\"\
              }\
            },\
            {\
              \"inline_data\": {\
                \"mime_type\":\"image/png\",\
                \"data\": \"$IMG2_BASE64\"\
              }\
            },\
            {\"text\": \"Take the first image of the woman with brown hair, blue eyes, and a neutral expression. Add the logo from the second image onto her black t-shirt. Ensure the woman's face and features remain completely unchanged. The logo should look like it's naturally printed on the fabric, following the folds of the shirt.\"}\
        ]\
      }]
    }"  \
  | grep -o '"data": "[^"]*"' \
  | cut -d'"' -f4 \
  | base64 --decode > woman_with_logo.png

```

|     |     |     |
| --- | --- | --- |
| Input 1 | Input 2 | Output |
| ![A professional headshot of a woman with brown hair and blue eyes...](https://ai.google.dev/static/gemini-api/docs/images/woman.png)A professional headshot of a woman with brown hair and blue eyes... | ![A simple, modern logo with the letters 'G' and 'A'...](https://ai.google.dev/static/gemini-api/docs/images/logo.png)A simple, modern logo with the letters 'G' and 'A'... | ![Take the first image of the woman with brown hair, blue eyes, and a neutral expression...](https://ai.google.dev/static/gemini-api/docs/images/woman_with_logo.png)Take the first image of the woman with brown hair, blue eyes, and a neutral expression... |

### Best Practices

To elevate your results from good to great, incorporate these professional
strategies into your workflow.

- **Be Hyper-Specific:** The more detail you provide, the more control you
have. Instead of "fantasy armor," describe it: "ornate elven plate armor, etched
with silver leaf patterns, with a high collar and pauldrons shaped like falcon
wings."
- **Provide Context and Intent:** Explain the _purpose_ of the image. The
model's understanding of context will influence the final output. For example,
"Create a logo for a high-end, minimalist skincare brand" will yield better
results than just "Create a logo."
- **Iterate and Refine:** Don't expect a perfect image on the first try. Use
the conversational nature of the model to make small changes. Follow up with
prompts like, "That's great, but can you make the lighting a bit warmer?" or
"Keep everything the same, but change the character's expression to be more
serious."
- **Use Step-by-Step Instructions:** For complex scenes with many elements,
break your prompt into steps. "First, create a background of a serene, misty
forest at dawn. Then, in the foreground, add a moss-covered ancient stone altar.
Finally, place a single, glowing sword on top of the altar."
- **Use "Semantic Negative Prompts":** Instead of saying "no cars," describe
the desired scene positively: "an empty, deserted street with no signs of
traffic."
- **Control the Camera:** Use photographic and cinematic language to control
the composition. Terms like `wide-angle shot`, `macro shot`, `low-angle
perspective`.

## Limitations

- For best performance, use the following languages: EN, es-MX, ja-JP, zh-CN,
hi-IN.
- Image generation does not support audio or video inputs.
- The model won't always follow the exact number of image outputs that the
user explicitly asks for.
- The model works best with up to 3 images as an input.
- When generating text for an image, Gemini works best if you first generate
the text and then ask for an image with the text.
- Uploading images of children is not currently supported in EEA, CH, and UK.
- All generated images include a [SynthID watermark](https://ai.google.dev/responsible/docs/safeguards/synthid).

## Optional configurations

You can optionally configure the response modalities and aspect ratio of the
model's output in the `config` field of `generate_content` calls.

### Output types

The model defaults to returning text and image responses
(i.e. `response_modalities=['Text', 'Image']`).
You can configure the response to return only images without text using
`response_modalities=['Image']`.

[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt],
    config=types.GenerateContentConfig(
        response_modalities=['Image']
    )
)

```

```
const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
    config: {
        responseModalities: ['Image']
    }
  });

```

```
result, _ := client.Models.GenerateContent(
    ctx,
    "gemini-2.5-flash-image",
    genai.Text("Create a picture of a nano banana dish in a " +
                " fancy restaurant with a Gemini theme"),
    &genai.GenerateContentConfig{
        ResponseModalities: "Image",
    },
  )

```

```
-d '{
  "contents": [{\
    "parts": [\
      {"text": "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"}\
    ]\
  }],
  "generationConfig": {
    "responseModalities": ["Image"]
  }
}' \

```

### Aspect ratios

The model defaults to matching the output image size to that of your input
image, or otherwise generates 1:1 squares.
You can control the aspect ratio of the output image using the `aspect_ratio`
field under `image_config` in the response request, shown here:

[Python](https://ai.google.dev/gemini-api/docs/image-generation#python)[JavaScript](https://ai.google.dev/gemini-api/docs/image-generation#javascript)[Go](https://ai.google.dev/gemini-api/docs/image-generation#go)[REST](https://ai.google.dev/gemini-api/docs/image-generation#rest)More

```
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt],
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
        )
    )
)

```

```
const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image",
    contents: prompt,
    config: {
      imageConfig: {
        aspectRatio: "16:9",
      },
    }
  });

```

```
result, _ := client.Models.GenerateContent(
    ctx,
    "gemini-2.5-flash-image",
    genai.Text("Create a picture of a nano banana dish in a " +
                " fancy restaurant with a Gemini theme"),
    &genai.GenerateContentConfig{
        ImageConfig: &genai.ImageConfig{
          AspectRatio: "16:9",
        },
    }
  )

```

```
-d '{
  "contents": [{\
    "parts": [\
      {"text": "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"}\
    ]\
  }],
  "generationConfig": {
    "imageConfig": {
      "aspectRatio": "16:9"
    }
  }
}' \

```

The different ratios available and the size of the image generated are listed in
this table:

| Aspect ratio | Resolution | Tokens |
| --- | --- | --- |
| 1:1 | 1024x1024 | 1290 |
| 2:3 | 832x1248 | 1290 |
| 3:2 | 1248x832 | 1290 |
| 3:4 | 864x1184 | 1290 |
| 4:3 | 1184x864 | 1290 |
| 4:5 | 896x1152 | 1290 |
| 5:4 | 1152x896 | 1290 |
| 9:16 | 768x1344 | 1290 |
| 16:9 | 1344x768 | 1290 |
| 21:9 | 1536x672 | 1290 |

## When to use Imagen

In addition to using Gemini's built-in image generation capabilities, you can
also access [Imagen](https://ai.google.dev/gemini-api/docs/imagen), our specialized image generation
model, through the Gemini API.

| Attribute | Imagen | Gemini Native Image |
| --- | --- | --- |
| Strengths | Most capable image generation model to date. Recommended for photorealistic images, sharper clarity, improved spelling and typography. | **Default recommendation.**<br>Unparalleled flexibility, contextual understanding, and simple, mask-free editing. Uniquely capable of multi-turn conversational editing. |
| Availability | Generally available | Preview (Production usage allowed) |
| Latency | **Low**. Optimized for near-real-time performance. | Higher. More computation is required for its advanced capabilities. |
| Cost | Cost-effective for specialized tasks. $0.02/image to $0.12/image | Token-based pricing. $30 per 1 million tokens for image output (image output tokenized at 1290 tokens per image flat, up to 1024x1024px) |
| Recommended tasks | - Image quality, photorealism, artistic detail, or specific styles (e.g., impressionism, anime) are top priorities.<br>- Infusing branding, style, or generating logos and product designs.<br>- Generating advanced spelling or typography. | - Interleaved text and image generation to seamlessly blend text and images.<br>- Combine creative elements from multiple images with a single prompt.<br>- Make highly specific edits to images, modify individual elements with simple language commands, and iteratively work on an image.<br>- Apply a specific design or texture from one image to another while preserving the original subject's form and details. |

Imagen 4 should be your go-to model starting to generate images with
Imagen. Choose Imagen 4 Ultra for advanced use-cases or
when you need the best image quality (note that can only generate one image at
a time).

## What's next

- Find more examples and code samples in the [cookbook guide](https://colab.sandbox.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Image_out.ipynb).
- Check out the [Veo guide](https://ai.google.dev/gemini-api/docs/video) to learn how to generate
videos with the Gemini API.
- To learn more about Gemini models, see [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini).

Was this helpful?



 Send feedback



Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-10-02 UTC.


Need to tell us more?






\[\[\["Easy to understand","easyToUnderstand","thumb-up"\],\["Solved my problem","solvedMyProblem","thumb-up"\],\["Other","otherUp","thumb-up"\]\],\[\["Missing the information I need","missingTheInformationINeed","thumb-down"\],\["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"\],\["Out of date","outOfDate","thumb-down"\],\["Samples / code issue","samplesCodeIssue","thumb-down"\],\["Other","otherDown","thumb-down"\]\],\["Last updated 2025-10-02 UTC."\],\[\],\[\]\]
