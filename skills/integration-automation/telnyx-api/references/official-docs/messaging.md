[Skip to main content](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#__docusaurus_skipToContent_fallback)

# Ask our

AI AssistantRead more [here](https://support.telnyx.com/en/articles/8020222-mission-control-portal-ai-chat-support).

Hello, how can I help you?

09:06

How do I set up a SIP trunk?

PoweredbyTelnyx

On this page

![Copy icon](https://developers.telnyx.com/img/icons/copy.svg)Copy for LLM![File text icon](https://developers.telnyx.com/img/icons/file-text.svg)View as Markdown

\| [Python](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#python) \| [PHP](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#php) \| [Node](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#node) \| [.NET](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#net) \| [Ruby](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#ruby) \|

* * *

## [Python ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#python "Direct link to Python")

⏱ **30 minutes build time**

### [Introduction ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#introduction "Direct link to Introduction")

Telnyx's messaging API supports both MMS and SMS messsages. Inbound multimedia messaging (MMS) messages include an attachment link in the webhook. The link and corresponding media should be treated as ephemeral and you should save any important media to a media storage (such as AWS S3) of your own.

#### [What you can do ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#what-you-can-do "Direct link to What you can do")

At the end of this tutorial you'll have an application that:

- Receives an inbound message (SMS or MMS)
- Iterates over any media attachments and downloads the remote attachment locally
- Uploads the same attachment to AWS S3
- Sends the attachments back to the same phone number that originally sent the message

### [Pre-reqs & technologies ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#pre-reqs--technologies "Direct link to Pre-reqs & technologies")

- Completed or familiar with the [Receiving SMS & MMS Quickstart](https://developers.telnyx.com/docs/messaging/messages/receive-message)
- A working [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS.
- Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/development/ngrok-setup))
- [Familiarity with Flask](https://flask.palletsprojects.com/en/2.2.x/)
- [Python & PIP](https://developers.telnyx.com/development/developer-setup#python) installed
- AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for more information.
- Previously created S3 bucket with public permissions available.

### [Setup ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup "Direct link to Setup")

#### [Telnyx Portal configuration ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#telnyx-portal-configuration "Direct link to Telnyx Portal configuration")

Be sure to have a [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS and webhook URL pointing to your service (using ngrok or similar)

#### [Install packages via PIP ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#install-packages-via-pip "Direct link to Install packages via PIP")

```bash
pip install telnyx
pip install boto3
pip install flask
pip install dotenv
pip install requests
```

note

After pasting the above content, Kindly check and remove any new line added

This will create `Pipfile` file with the packages needed to run the application.

#### [Setting environment variables ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setting-environment-variables "Direct link to Setting environment variables")

The following environmental variables need to be set

|     |     |
| --- | --- |
| Variable | Description |
| `TELNYX_API_KEY` | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys) |
| `TELNYX_PUBLIC_KEY` | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key) |
| `TELNYX_APP_PORT` | **Defaults to `8000`** The port the app will be served |
| `AWS_PROFILE` | Your AWS profile as set in `~/.aws` |
| `AWS_REGION` | The region of your S3 bucket |
| `TELNYX_MMS_S3_BUCKET` | The name of the bucket to upload the media attachments |

#### [.env file ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#env-file "Direct link to .env file")

This app uses the excellent [python-dotenv](https://github.com/theskumar/python-dotenv) package to manage environment variables.

Make a copy of the file below, add your credentials, and save as `.env` in the root directory.

```bash
TELNYX_API_KEY=
TELNYX_PUBLIC_KEY=
TENYX_APP_PORT=8000
AWS_PROFILE=
AWS_REGION=
TELNYX_MMS_S3_BUCKET=
```

note

After pasting the above content, Kindly check and remove any new line added

### [Code-along ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#code-along "Direct link to Code-along")

We'll use a singe `app.py` file to build the MMS application.

```bash
touch app.py
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Setup Flask Server ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-flask-server "Direct link to Setup Flask Server")

```python
import telnyx
import os
from urllib.parse import urlunsplit, urlparse
import json
import requests
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, Response
from dotenv import load_dotenv

app = Flask(__name__)

## Will add more flask code
## ..
## ..

## Load env vars and start flask server
if __name__ == "__main__":
    load_dotenv()
    TELNYX_MMS_S3_BUCKET = os.getenv("TELNYX_MMS_S3_BUCKET")
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    TELNYX_APP_PORT = os.getenv("TELNYX_APP_PORT")
    app.run(port=TELNYX_APP_PORT)
```

note

After pasting the above content, Kindly check and remove any new line added

### [Receiving Webhooks ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#receiving-webhooks "Direct link to Receiving Webhooks")

Now that you have setup your auth token, phone number, and connection, you can begin to use the API Library to send/receive SMS & MMS messages. First, you will need to setup an endpoint to receive webhooks for inbound messages & outbound message Delivery Receipts (DLR).

#### [Basic routing & functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#basic-routing--functions "Direct link to Basic routing & functions")

The basic overview of the application is as follows:

1. Verify webhook & create TelnyxEvent
2. Extract information from the webhook
3. Iterate over any media and download/re-upload to S3 for each attachment
4. Send the message back to the phone number from which it came
5. Acknowledge the status update (DLR) of the outbound message

#### [Media download & upload functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#media-download--upload-functions "Direct link to Media download & upload functions")

Before diving into the inbound message handler, first we'll create a few functions to manage our attachments.

- `download_file` saves the content from a URL to disk
- `upload_file` uploads the file passed to AWS S3 (and makes object public)
- `media_downloader_uploader` calls the download function and passes result to upload function

```python
def download_file(url):
    r = requests.get(url, allow_redirects=True)
    file_name = os.path.basename(urlparse(url).path)
    open(file_name, "wb").write(r.content)
    return file_name

def upload_file(file_path):
    global TELNYX_MMS_S3_BUCKET
    s3_client = boto3.client("s3")
    file_name = os.path.basename(file_path)
    try:
        extra_args = {
            "ContentType": "application/octet-stream",
            "ACL": "public-read"
        }
        s3_client.upload_file(
            file_path,
            TELNYX_MMS_S3_BUCKET,
            file_name,
            ExtraArgs=extra_args)
    except ClientError as e:
        print("Error uploading file to S3")
        print(e)
        quit()
    return f"https://{TELNYX_MMS_S3_BUCKET}.s3.amazonaws.com/{file_name}"

def media_downloader_uploader(url):
    file_location = download_file(url)
    file_url = upload_file(file_location)
    return file_url
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Inbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#inbound-message-handling "Direct link to Inbound message handling")

Now that we have the functions to manage the media, we can start receiving inbound MMS's

The flow of our function is (at a high level):

1. Extract relevant information from the webhook
2. Build the `webhook_url` to direct the DLR to a new endpoint
3. Iterate over any attachments/media and call our `media_downloader_uploader` function
4. Send the outbound message back to the original sender with the media attachments

```python
@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    dlr_url = urlunsplit((
        request.scheme,
        request.host,
        "/messaging/outbound",
        "", ""))
    to_number = body["data"]["payload"]["to"][0]["phone_number"]
    from_number = body["data"]["payload"]["from"]["phone_number"]
    medias = body["data"]["payload"]["media"]
    media_urls = list(map(lambda media: media_downloader_uploader(media["url"]), medias))
    try:
        telnyx_response = telnyx.Message.create(
            from_=to_number,
            to=from_number,
            text="👋 Hello World",
            media_urls=media_urls,
            webhook_url=dlr_url,
            use_profile_webhooks=False
        )
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Outbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#outbound-message-handling "Direct link to Outbound message handling")

As we defined our `webhook_url` path to be `/messaging/outbound` we'll need to create a function that accepts a POST request to that path within messaging.js.

```python
@app.route("/messaging/outbound", methods=["POST"])
def outbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received message DLR with ID: {message_id}")
    return Response(status=200)
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Final app.py ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#final-apppy "Direct link to Final app.py")

All together the app.py should look something like:

```python
import telnyx
import os
from urllib.parse import urlunsplit, urlparse
import json
import requests
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, Response
from dotenv import load_dotenv

app = Flask(__name__)

def download_file(url):
    r = requests.get(url, allow_redirects=True)
    file_name = os.path.basename(urlparse(url).path)
    open(file_name, "wb").write(r.content)
    return file_name

def upload_file(file_path):
    global TELNYX_MMS_S3_BUCKET
    s3_client = boto3.client("s3")
    file_name = os.path.basename(file_path)
    try:
        extra_args = {
            "ContentType": "application/octet-stream",
            "ACL": "public-read"
        }
        s3_client.upload_file(
            file_path,
            TELNYX_MMS_S3_BUCKET,
            file_name,
            ExtraArgs=extra_args)
    except ClientError as e:
        print("Error uploading file to S3")
        print(e)
        quit()
    return f"https://{TELNYX_MMS_S3_BUCKET}.s3.amazonaws.com/{file_name}"

def media_downloader_uploader(url):
    file_location = download_file(url)
    file_url = upload_file(file_location)
    return file_url

@app.route("/messaging/inbound", methods=["POST"])
def inbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received inbound message with ID: {message_id}")
    dlr_url = urlunsplit((
        request.scheme,
        request.host,
        "/messaging/outbound",
        "", ""))
    to_number = body["data"]["payload"]["to"][0]["phone_number"]
    from_number = body["data"]["payload"]["from"]["phone_number"]
    medias = body["data"]["payload"]["media"]
    media_urls = list(map(lambda media: media_downloader_uploader(media["url"]), medias))
    try:
        telnyx_response = telnyx.Message.create(
            from_=to_number,
            to=from_number,
            text="👋 Hello World",
            media_urls=media_urls,
            webhook_url=dlr_url,
            use_profile_webhooks=False
        )
        print(f"Sent message with id: {telnyx_response.id}")
    except Exception as e:
        print("Error sending message")
        print(e)
    return Response(status=200)

@app.route("/messaging/outbound", methods=["POST"])
def outbound_message():
    body = json.loads(request.data)
    message_id = body["data"]["payload"]["id"]
    print(f"Received message DLR with ID: {message_id}")
    return Response(status=200)

if __name__ == "__main__":
    load_dotenv()
    TELNYX_MMS_S3_BUCKET = os.getenv("TELNYX_MMS_S3_BUCKET")
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
    TELNYX_APP_PORT = os.getenv("TELNYX_APP_PORT")
    app.run(port=TELNYX_APP_PORT)
```

note

After pasting the above content, Kindly check and remove any new line added

### [Usage ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#usage "Direct link to Usage")

Start the server `python app.py`

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](https://developers.telnyx.com/development/ngrok-setup) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings in the Mission Control Portal. To do this, click the edit symbol \[✎\] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

##### [Callback URLs For Telnyx Applications ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#callback-urls-for-telnyx-applications "Direct link to Callback URLs For Telnyx Applications")

|     |     |
| --- | --- |
| Callback Type | URL |
| Inbound Message Callback | `{ngrok-url}/messaging/inbound` |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |

Once everything is setup, you should now be able to:

- Text your phone number and receive a response!
- Send a picture to your phone number and get that same picture right back!

## [PHP ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#php "Direct link to PHP")

⏱ **30 minutes build time**

### [Introduction to MMS ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#introduction-to-mms "Direct link to Introduction to MMS")

Telnyx's messaging API supports both MMS and SMS messsages. Inbound multimedia messaging (MMS) messages include an attachment link in the webhook. The link and corresponding media should be treated as ephemeral and you should save any important media to a media storage (such as AWS S3) of your own.

### [What you can do with this Tutorial ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#what-you-can-do-with-this-tutorial "Direct link to What you can do with this Tutorial")

At the end of this tutorial you'll have an application that:

- Receives an inbound message (SMS or MMS)
- Iterates over any media attachments and downloads the remote attachment locally
- Uploads the same attachment to AWS S3
- Sends the attachments back to the same phone number that originally sent the message

### [Pre-reqs & technologies for MMS ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#pre-reqs--technologies-for-mms "Direct link to Pre-reqs & technologies for MMS")

- Completed or familiar with the [Receiving SMS & MMS Quickstart](https://developers.telnyx.com/docs/messaging/messages/receive-message)
- A working [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS.
- [PHP](https://developers.telnyx.com/development/developer-setup#php) installed with [Composer](https://getcomposer.org/)
- [Familiarity with Slim](https://www.slimframework.com/)
- Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/development/ngrok-setup))
- AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://aws.amazon.com/sdk-for-php/) for more information.
- Previously created S3 bucket with public permissions available.

### [Setup Your MMS Application ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-your-mms-application "Direct link to Setup Your MMS Application")

#### [Telnyx Portal configuration ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#telnyx-portal-configuration-1 "Direct link to Telnyx Portal configuration")

Be sure to have a [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS and webhook URL pointing to your service (using ngrok or similar)

#### [Install packages via composer ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#install-packages-via-composer "Direct link to Install packages via composer")

```bash
composer require vlucas/phpdotenv
composer require telnyx/telnyx-php
composer require slim/http
composer require slim/psr7
composer require slim/slim
composer require aws/aws-sdk-php
composer require jakeasmith/http_build_url
```

note

After pasting the above content, Kindly check and remove any new line added

This will create `composer.json` file with the packages needed to run the application.

#### [Setting environment variables ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setting-environment-variables-1 "Direct link to Setting environment variables")

The following environmental variables need to be set

|     |     |
| --- | --- |
| Variable | Description |
| `TELNYX_API_KEY` | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys) |
| `TELNYX_PUBLIC_KEY` | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key) |
| `TELNYX_APP_PORT` | **Defaults to `8000`** The port the app will be served |
| `AWS_PROFILE` | Your AWS profile as set in `~/.aws` |
| `AWS_REGION` | The region of your S3 bucket |
| `TELNYX_MMS_S3_BUCKET` | The name of the bucket to upload the media attachments |

#### [.env file ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#env-file-1 "Direct link to .env file")

This app uses the excellent [phpenv](https://github.com/vlucas/phpdotenv) package to manage environment variables.

Make a copy of the file below, add your credentials, and save as `.env` in the root directory.

```bash
TELNYX_API_KEY=
TELNYX_PUBLIC_KEY=
TENYX_APP_PORT=8000
AWS_PROFILE=
AWS_REGION=
TELNYX_MMS_S3_BUCKET=
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Code-along ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#code-along-1 "Direct link to Code-along")

Now create a folder public and a file in the public folderindex.php, then write the following to setup the telnyx library.

```bash
mkdir public
touch public/index.php
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Setup Slim Server and instantiate Telnyx ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-slim-server-and-instantiate-telnyx "Direct link to Setup Slim Server and instantiate Telnyx")

```php
<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;
use Slim\Factory\AppFactory;
use Telnyx\Message;
use Telnyx\Webhook;
use Aws\S3\S3Client;
use Aws\S3\Exception\S3Exception;

require __DIR__ . '/../vendor/autoload.php';

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__, '../.env');
$dotenv->load();

$TELNYX_API_KEY       = $_ENV['TELNYX_API_KEY'];
$TELNYX_PUBLIC_KEY    = $_ENV['TELNYX_PUBLIC_KEY'];
$AWS_REGION           = $_ENV['AWS_REGION'];
$TELNYX_MMS_S3_BUCKET = $_ENV['TELNYX_MMS_S3_BUCKET'];
$AWS_PROFILE          = $_ENV['AWS_PROFILE'];

Telnyx\Telnyx::setApiKey($TELNYX_API_KEY);
Telnyx\Telnyx::setPublicKey($TELNYX_PUBLIC_KEY);
// Instantiate App
$app = AppFactory::create();

// Add error middleware
$app->addErrorMiddleware(true, true, true);
```

note

After pasting the above content, Kindly check and remove any new line added

### [Receiving Webhooks for SMS & MMS ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#receiving-webhooks-for-sms--mms "Direct link to Receiving Webhooks for SMS & MMS")

Now that you have setup your auth token, phone number, and connection, you can begin to use the API Library to send/receive SMS & MMS messages. First, you will need to setup an endpoint to receive webhooks for inbound messages & outbound message Delivery Receipts (DLR).

#### [Basic routing & functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#basic-routing--functions-1 "Direct link to Basic routing & functions")

The basic overview of the application is as follows:

1. Verify webhook & create TelnyxEvent
2. Extract information from the webhook
3. Iterate over any media and download/re-upload to S3 for each attachment
4. Send the message back to the phone number from which it came
5. Acknowledge the status update (DLR) of the outbound message

##### [Webhook validation middleware ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#webhook-validation-middleware "Direct link to Webhook validation middleware")

Telnyx signs each webhook that can be validated by checking the signature with your public key. This example adds the verification step as middleware to be included on all Telnyx endpoints.

```php
//Callback signature verification
$telnyxWebhookVerify = function (Request $request, RequestHandler $handler) {
    //Extract the raw contents
    $payload = $request->getBody()->getContents();
    //Grab the signature
    $sigHeader = $request->getHeader('HTTP_TELNYX_SIGNATURE_ED25519')[0];
    //Grab the timestamp
    $timeStampHeader = $request->getHeader('HTTP_TELNYX_TIMESTAMP')[0];
    //Construct the Telnyx event which will validate the signature and timestamp
    $telnyxEvent = \Telnyx\Webhook::constructEvent($payload, $sigHeader, $timeStampHeader);
    //Add the event object to the request to keep context for future middleware
    $request = $request->withAttribute('telnyxEvent', $telnyxEvent);
    //Send to next middleware
    $response = $handler->handle($request);
    //return response back to Telnyx
    return $response;
};
```

note

After pasting the above content, Kindly check and remove any new line added

ℹ️ For more details on middleware see [Slim's documentation on Route Middleware](https://www.slimframework.com/docs/v4/objects/routing.html#route-middleware)

#### [Media Download & Upload Functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#media-download--upload-functions-1 "Direct link to Media Download & Upload Functions")

Before diving into the inbound message handler, first we'll create a few functions to manage our attachments.

- `downloadMedia` saves the content from a URL to disk
- `uploadMedia` uploads the file passed to AWS S3 (and makes object public)
- `downloadUpload` accepts an object and calls both the `downloadMedia` & `uploadMedia` returning the final S3 URL

```php
function downloadMedia(String $url){
    $fileName = basename($url);
    file_put_contents($fileName,file_get_contents($url));
    return $fileName;
}

function uploadMedia(String $fileLocation){
    global $AWS_REGION, $TELNYX_MMS_S3_BUCKET;
    $s3 = new S3Client([\
        'version' => 'latest',\
        'region'  => $AWS_REGION\
    ]);
    $keyName = basename($fileLocation);
    try {
        // Upload data.
        $result = $s3->putObject([\
            'Bucket' => $TELNYX_MMS_S3_BUCKET,\
            'Key'    => $keyName,\
            'SourceFile' => $fileLocation,\
            'ACL'    => 'public-read'\
        ]);

        // The URL to the object.
        $url =  $result['ObjectURL'];
        return $url;
    } catch (S3Exception $e) {
        echo $e->getMessage() . PHP_EOL;
    }
}

function downloadUpload($media) {
    $fileLocation = downloadMedia($media['url']);
    $mediaUrl = uploadMedia($fileLocation);
    return $mediaUrl;
}
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Inbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#inbound-message-handling-1 "Direct link to Inbound message handling")

Now that we have the functions to manage the media, we can start receiving inbound MMS's

The flow of our function is (at a high level):

1. Extract relevant information from the webhook
2. Build the `webhook_url` to direct the DLR to a new endpoint
3. Iterate over any attachments/media and call our `downloadUpload` function
4. Send the outbound message back to the original sender with the media attachments

```php
$app->post('/messaging/inbound', function (Request $request, Response $response) {
    $body = $request->getParsedBody();
    $payload = $body['data']['payload'];
    $toNumber = $payload['to'][0]['phone_number'];
    $fromNumber = $payload['from']['phone_number'];
    $medias = $payload['media'];
    $dlrUrl = http_build_url([\
        'scheme' => $request->getUri()->getScheme(),\
        'host' => $request->getUri()->getHost(),\
        'path' => '/messaging/outbound'\
    ]);
    $mediaUrls = array_map('downloadUpload', $medias);
    try {
        $new_message = Message::Create([\
            'from' => $toNumber,\
            'to' => $fromNumber,\
            'text' => 'Hello, world!',\
            'media_urls' => $mediaUrls,\
            'use_profile_webhooks' => false,\
            'webhook_url' => $dlrUrl\
            ]);
        $messageId = $new_message->id;
        echo 'Sent message with ID: ', $messageId;
    }
    catch (Exception $e) {
        echo 'Caught exception: ',  $e->getMessage(), "\n";
    }
    return $response->withStatus(200);
})->add($telnyxWebhookVerify);
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Inbound Message Handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#inbound-message-handling-2 "Direct link to Inbound Message Handling")

As we defined our `webhook_url` path to be `/messaging/outbound` we'll need to create a function that accepts a POST request to that path.

```php
$app->post('/messaging/outbound', function (Request $request, Response $response) {
    // Handle outbound DLR
    return $response->withStatus(200);
})->add($telnyxWebhookVerify);
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Final index.php ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#final-indexphp "Direct link to Final index.php")

All together the PHP samples should look something like:

```php
<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;
use Slim\Factory\AppFactory;
use Telnyx\Message;
use Telnyx\Webhook;
use Aws\S3\S3Client;
use Aws\S3\Exception\S3Exception;

require __DIR__ . '/../vendor/autoload.php';

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__, '../.env');
$dotenv->load();

$TELNYX_API_KEY       = $_ENV['TELNYX_API_KEY'];
$TELNYX_PUBLIC_KEY    = $_ENV['TELNYX_PUBLIC_KEY'];
$AWS_REGION           = $_ENV['AWS_REGION'];
$TELNYX_MMS_S3_BUCKET = $_ENV['TELNYX_MMS_S3_BUCKET'];
$AWS_PROFILE          = $_ENV['AWS_PROFILE'];

Telnyx\Telnyx::setApiKey($TELNYX_API_KEY);
Telnyx\Telnyx::setPublicKey($TELNYX_PUBLIC_KEY);
// Instantiate App
$app = AppFactory::create();

// Add error middleware
$app->addErrorMiddleware(true, true, true);

//Callback signature verification
$telnyxWebhookVerify = function (Request $request, RequestHandler $handler) {
    $payload = $request->getBody()->getContents();
    $sigHeader = $request->getHeader('HTTP_TELNYX_SIGNATURE_ED25519')[0];
    $timeStampHeader = $request->getHeader('HTTP_TELNYX_TIMESTAMP')[0];
    $telnyxEvent = Webhook::constructEvent($payload, $sigHeader, $timeStampHeader);
    $request = $request->withAttribute('telnyxEvent', $telnyxEvent);
    $response = $handler->handle($request);
    return $response;
};

function downloadMedia(String $url){
    $fileName = basename($url);
    file_put_contents($fileName,file_get_contents($url));
    return $fileName;
}

function uploadMedia(String $fileLocation){
    global $AWS_REGION, $TELNYX_MMS_S3_BUCKET;
    $s3 = new S3Client([\
        'version' => 'latest',\
        'region'  => $AWS_REGION\
    ]);
    $keyName = basename($fileLocation);
    try {
        // Upload data.
        $result = $s3->putObject([\
            'Bucket' => $TELNYX_MMS_S3_BUCKET,\
            'Key'    => $keyName,\
            'SourceFile' => $fileLocation,\
            'ACL'    => 'public-read'\
        ]);

        // Print the URL to the object.
        $url =  $result['ObjectURL'];
        return $url;
    } catch (S3Exception $e) {
        echo $e->getMessage() . PHP_EOL;
    }
}

function downloadUpload($media) {
    $fileLocation = downloadMedia($media['url']);
    $mediaUrl = uploadMedia($fileLocation);
    return $mediaUrl;
}

// Add routes
$app->post('/messaging/inbound', function (Request $request, Response $response) {
    $body = $request->getParsedBody();
    $payload = $body['data']['payload'];
    $toNumber = $payload['to'][0]['phone_number'];
    $fromNumber = $payload['from']['phone_number'];
    $medias = $payload['media'];
    $dlrUrl = http_build_url([\
        'scheme' => $request->getUri()->getScheme(),\
        'host' => $request->getUri()->getHost(),\
        'path' => '/messaging/outbound'\
    ]);
    $mediaUrls = array_map('downloadUpload', $medias);
    try {
        $new_message = Message::Create([\
            'from' => $toNumber,\
            'to' => $fromNumber,\
            'text' => 'Hello, world!',\
            'media_urls' => $mediaUrls,\
            'use_profile_webhooks' => false,\
            'webhook_url' => $dlrUrl\
            ]);
        $messageId = $new_message->id;
        echo 'Sent message with ID: ', $messageId;
    }
    catch (Exception $e) {
        echo 'Caught exception: ',  $e->getMessage(), "\n";
    }
    return $response->withStatus(200);
})->add($telnyxWebhookVerify);

$app->post('/messaging/outbound', function (Request $request, Response $response) {
    // Handle outbound DLR
    return $response->withStatus(200);
})->add($telnyxWebhookVerify);
$app->run();
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Usage ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#usage-1 "Direct link to Usage")

Start the server `php -S localhost:8000 -t public`

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](https://developers.telnyx.com/development/ngrok-setup) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings in the Mission Control Portal. To do this, click the edit symbol \[✎\] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your slim-php server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

##### [Callback URLs For Telnyx Applications ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#callback-urls-for-telnyx-applications-1 "Direct link to Callback URLs For Telnyx Applications")

|     |     |
| --- | --- |
| Callback Type | URL |
| Inbound Message Callback | `{ngrok-url}/messaging/inbound` |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |

Once everything is setup, you should now be able to:

- Text your phone number and receive a response!
- Send a picture to your phone number and get that same picture right back!

## [Node ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#node "Direct link to Node")

⏱ **30 minutes build time** \|\| [Github Repo](https://github.com/team-telnyx/demo-node-telnyx/tree/master/express-messaging)

### [Introduction ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#introduction-1 "Direct link to Introduction")

Telnyx's messaging API supports both MMS and SMS messsages. Inbound multimedia messaging (MMS) messages include an attachment link in the webhook. The link and corresponding media should be treated as ephemeral and you should save any important media to a media storage (such as AWS S3) of your own.

### [What you can do ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#what-you-can-do-1 "Direct link to What you can do")

At the end of this tutorial you'll have an application that:

- Receives an inbound message (SMS or MMS)
- Iterates over any media attachments and downloads the remote attachment locally
- Uploads the same attachment to AWS S3
- Sends the attachments back to the same phone number that originally sent the message

### [Pre-reqs & technologies ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#pre-reqs--technologies-1 "Direct link to Pre-reqs & technologies")

- Completed or familiar with the [Receiving SMS & MMS Quickstart](https://developers.telnyx.com/docs/messaging/messages/receive-message#node)
- A working [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS.
- [Node & NPM](https://developers.telnyx.com/development/developer-setup#node) installed
- [Familiarity with Express](https://expressjs.com/)
- Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/development/ngrok-setup))
- AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://docs.aws.amazon.com/sdk-for-javascript/index.html) for more information.
- Previously created S3 bucket with public permissions available.

### [Setup ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-1 "Direct link to Setup")

#### [Telnyx portal configuration ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#telnyx-portal-configuration-2 "Direct link to Telnyx portal configuration")

Be sure to have a [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS and webhook URL pointing to your service (using ngrok or similar)

#### [Install packages via NPM ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#install-packages-via-npm "Direct link to Install packages via NPM")

```bash
npm i aws-sdk
npm i axios
npm i dotenv
npm i express
npm i telnyx
```

note

After pasting the above content, Kindly check and remove any new line added

This will create `package.json` file with the packages needed to run the application.

#### [Setting environment variables ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setting-environment-variables-2 "Direct link to Setting environment variables")

The following environmental variables need to be set

|     |     |
| --- | --- |
| Variable | Description |
| `TELNYX_API_KEY` | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys) |
| `TELNYX_PUBLIC_KEY` | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key) |
| `TELNYX_APP_PORT` | **Defaults to `8000`** The port the app will be served |
| `AWS_PROFILE` | Your AWS profile as set in `~/.aws` |
| `AWS_REGION` | The region of your S3 bucket |
| `TELNYX_MMS_S3_BUCKET` | The name of the bucket to upload the media attachments |

#### [.env file ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#env-file-2 "Direct link to .env file")

This app uses the excellent [dotenv](https://github.com/bkeepers/dotenv) package to manage environment variables.

Make a copy of the file below, add your credentials, and save as `.env` in the root directory.

```bash
TELNYX_API_KEY=
TELNYX_PUBLIC_KEY=
TENYX_APP_PORT=8000
AWS_PROFILE=
AWS_REGION=
TELNYX_MMS_S3_BUCKET=
```

note

After pasting the above content, Kindly check and remove any new line added

### [Code-along ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#code-along-2 "Direct link to Code-along")

We'll use a few `.js` files to build the MMS application. `index.js` as our entry point and `messaging.js` to contain our routes and controllers for the app.

```bash
touch index.js
touch messaging.js
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Setup Express Server ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-express-server "Direct link to Setup Express Server")

```js
// In index.js
import dotenv from "dotenv";
dotenv.config();

import express from 'express';
import config from './config';
import messaging from './messaging';
import Telnyx from 'telnyx';

const telnyx = new Telnyx("YOUR_API_KEY");

const app = express();

app.use(express.json());

app.use('/messaging', messaging);

app.listen(config.TELNYX_APP_PORT);
console.log(`Server listening on port ${config.TELNYX_APP_PORT}`);
```

note

After pasting the above content, Kindly check and remove any new line added

### [Receiving Webhooks ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#receiving-webhooks-1 "Direct link to Receiving Webhooks")

Now that you have setup your auth token, phone number, and connection, you can begin to use the API Library to send/receive SMS & MMS messages. First, you will need to setup an endpoint to receive webhooks for inbound messages & outbound message Delivery Receipts (DLR).

#### [Basic routing & functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#basic-routing--functions-2 "Direct link to Basic routing & functions")

The basic overview of the application is as follows:

1. Verify webhook & create TelnyxEvent
2. Extract information from the webhook
3. Iterate over any media and download/re-upload to S3 for each attachment
4. Send the message back to the phone number from which it came
5. Acknowledge the status update (DLR) of the outbound message

#### [Webhook validation middleware ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#webhook-validation-middleware-1 "Direct link to Webhook validation middleware")

Telnyx signs each webhook that can be validated by checking the signature with your public key. This example adds the verification step as middleware to be included on all Telnyx endpoints.

After declaring the `const app=express();` and before `app.use('/messaging', messaging);` add the following code to validate the webhook in indeed from Telnyx.

```js
// in index.js
const webhookValidator = (req, res, next) => {
  try {
    telnyx.webhooks.constructEvent(
      JSON.stringify(req.body, null, 2),
      req.header('telnyx-signature-ed25519'),
      req.header('telnyx-timestamp'),
      config.TELNYX_PUBLIC_KEY
    )
    next();
    return;
  }
  catch (e) {
    console.log(`Invalid webhook: ${e.message}`);
    return res.status(400).send(`Webhook Error: ${e.message}`);
  }
};

app.use(webhookValidator);
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Media Download & Upload Functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#media-download--upload-functions-2 "Direct link to Media Download & Upload Functions")

Before diving into the inbound message handler, first we'll create a few functions to manage our attachments inside the `messaging.js` file.

- `downloadFile` saves the content from a URL to disk
- `uploadFile` uploads the file passed to AWS S3 (and makes object public)
- Note that this application is demonstrating 2 topics at once, downloading & uploading. It could be improved by piping or streaming the data from Telnyx to S3 instead of saving to disk.

```javascript
// In messaging.js
import express from 'express';
import config from './config';
import fs from 'fs';
import axios from 'axios';
import AWS from 'aws-sdk';
import path from 'path';
import Telnyx from 'telnyx';
import url from 'url';

AWS.config.update({region: config.AWS_REGION});
const telnyx = new Telnyx("YOUR_API_KEY");
export const router = express.Router();

const uploadFile = async filePath => {
  const s3 = new AWS.S3({apiVersion: '2006-03-01'});
  const bucketName = config.TELNYX_MMS_S3_BUCKET;
  const fileName = path.basename(filePath);
  const fileStream = fs.createReadStream(filePath);
  return new Promise(async (resolve, reject) => {
    fileStream.once('error', reject);
    try {
      const s3UploadParams = {
        Bucket: bucketName,
        Key: fileName,
        Body: fileStream,
        ACL: 'public-read'
      }
      await s3.upload(s3UploadParams).promise();
      resolve(`https://${bucketName}.s3.amazonaws.com/${fileName}`);
    }
    catch (e) {
      reject(e);
    }
  });
};

const downloadFile = async url => {
  const fileLocation = path.resolve(__dirname, url.substring(url.lastIndexOf('/')+1));
  const response = await axios({
    method: "get",
    url: url,
    responseType: "stream"
  });
  response.data.pipe(fs.createWriteStream(fileLocation));
  return new Promise((resolve, reject) => {
    response.data.on('end', () => {resolve(fileLocation)} );
    response.data.on('error', reject);
  });
};
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Inbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#inbound-message-handling-3 "Direct link to Inbound message handling")

Now that we have the functions to manage the media, we can start receiving inbound MMS's

The flow of our function is (at a high level):

1. Extract relevant information from the webhook
2. Build the `webhook_url` to direct the DLR to a new endpoint
3. Iterate over any attachments/media and call our `download` & `upload` functions
4. Send the outbound message back to the original sender with the media attachments

```js
// In messaging.js
const inboundMessageController = async (req, res) => {
  res.sendStatus(200); // Play nice and respond to webhook
  const event = req.body.data;
  console.log(`Received inbound message with ID: ${event.payload.id}`)
  const dlrUrl = (new URL('/messaging/outbound', `${req.protocol}://${req.hostname}`)).href;
  const toNumber = event.payload.to[0].phone_number;
  const fromNumber = event.payload['from'].phone_number;
  const medias = event.payload.media;
  const mediaPromises = medias.map(async media => {
    const fileName = await downloadFile(media.url)
    return uploadFile(fileName);
  });
  const mediaUrls = await Promise.all(mediaPromises);
  try {
    const messageRequest = {
      from: toNumber,
      to: fromNumber,
      text: '👋 Hello World',
      media_urls: mediaUrls,
      webhook_url: dlrUrl,
      use_profile_webhooks: false
    }
    const telnyxResponse = await telnyx.messages.create(messageRequest);
    console.log(`Sent message with id: ${telnyxResponse.data.id}`);
  }
  catch (e)  {
    console.log('Error sending message');
    console.log(e);
  }

};
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Outbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#outbound-message-handling-1 "Direct link to Outbound message handling")

As we defined our `webhook_url` path to be `/messaging/outbound` we'll need to create a function that accepts a POST request to that path within messaging.js.

```js
// In messaging.js
const outboundMessageController = async (req, res) => {
  res.sendStatus(200); // Play nice and respond to webhook
  const event = req.body.data;
  console.log(`Received message DLR with ID: ${event.payload.id}`)
};
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Decare routes for inbound and outbound messaging ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#decare-routes-for-inbound-and-outbound-messaging "Direct link to Decare routes for inbound and outbound messaging")

At the bottom of `messaging.js` add the routes and point to the correct controller function

```js
router.route('/inbound')
    .post(inboundMessageController);

router.route('/outbound')
    .post(outboundMessageController);
```

note

After pasting the above content, Kindly check and remove any new line added

### [Final index.js ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#final-indexjs "Direct link to Final index.js")

All together the index.js should look something like:

```js
import 'dotenv/config';
dotenv.config();

import express from 'express';
import config from './config';
import Telnyx from 'telnyx';
import messaging from './messaging';

const telnyx = new Telnyx("YOUR_API_KEY");
const app = express();

const webhookValidator = (req, res, next) => {
  try {
    telnyx.webhooks.constructEvent(
      JSON.stringify(req.body, null, 2),
      req.header('telnyx-signature-ed25519'),
      req.header('telnyx-timestamp'),
      config.TELNYX_PUBLIC_KEY
    )
    next();
    return;
  }
  catch (e) {
    console.log(`Invalid webhook: ${e.message}`);
    return res.status(400).send(`Webhook Error: ${e.message}`);
  }
}

app.use(express.json());
app.use(webhookValidator);

app.use('/messaging', messaging);

app.listen(config.TELNYX_APP_PORT);
console.log(`Server listening on port ${config.TELNYX_APP_PORT}`);
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Final messaging.js ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#final-messagingjs "Direct link to Final messaging.js")

```js
import express  from 'express';
import config from './config';
import fs from 'fs';
import axios from 'axios';
import AWS from 'aws-sdk';
import path from 'path';
import url from 'url';
import Telnyx from 'telnyx';

AWS.config.update({region: config.AWS_REGION});

const telnyx = new Telnyx("YOUR_API_KEY");
export const router = express.Router();

const toBase64 = data => (new Buffer.from(data)).toString('base64');
const fromBase64 = data => (new Buffer.from(data, 'base64')).toString();

const outboundMessageController = async (req, res) => {
  res.sendStatus(200); // Play nice and respond to webhook
  const event = req.body.data;
  console.log(`Received message DLR with ID: ${event.payload.id}`)
}

const uploadFile = async filePath => {
  const s3 = new AWS.S3({apiVersion: '2006-03-01'});
  const bucketName = config.TELNYX_MMS_S3_BUCKET;
  const fileName = path.basename(filePath);
  const fileStream = fs.createReadStream(filePath);
  return new Promise(async (resolve, reject) => {
    fileStream.once('error', reject);
    try {
      const s3UploadParams = {
        Bucket: bucketName,
        Key: fileName,
        Body: fileStream,
        ACL: 'public-read'
      }
      await s3.upload(s3UploadParams).promise();
      resolve(`https://${bucketName}.s3.amazonaws.com/${fileName}`);
    }
    catch (e) {
      reject(e);
    }
  });
};

const downloadFile = async url => {
  const fileLocation = path.resolve(__dirname, url.substring(url.lastIndexOf('/')+1));
  const response = await axios({
    method: "get",
    url: url,
    responseType: "stream"
  });
  response.data.pipe(fs.createWriteStream(fileLocation));
  return new Promise((resolve, reject) => {
    response.data.on('end', () => {resolve(fileLocation)} );
    response.data.on('error', reject);
  });
};

const inboundMessageController = async (req, res) => {
  res.sendStatus(200); // Play nice and respond to webhook
  const event = req.body.data;
  console.log(`Received inbound message with ID: ${event.payload.id}`)
  const dlrUrl = (new URL('/messaging/outbound', `${req.protocol}://${req.hostname}`)).href;
  const toNumber = event.payload.to[0].phone_number;
  const fromNumber = event.payload['from'].phone_number;
  const medias = event.payload.media;
  const mediaPromises = medias.map(async media => {
    const fileName = await downloadFile(media.url)
    return uploadFile(fileName);
  });
  const mediaUrls = await Promise.all(mediaPromises);
  try {
    const messageRequest = {
      from: toNumber,
      to: fromNumber,
      text: '👋 Hello World',
      media_urls: mediaUrls,
      webhook_url: dlrUrl,
      use_profile_webhooks: false
    }

    const telnyxResponse = await telnyx.messages.create(messageRequest);
    console.log(`Sent message with id: ${telnyxResponse.data.id}`);
  }
  catch (e)  {
    console.log('Error sending message');
    console.log(e);
  }

}

router.route('/inbound')
    .post(inboundMessageController);

router.route('/outbound')
    .post(outboundMessageController);
```

note

After pasting the above content, Kindly check and remove any new line added

### [Usage ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#usage-2 "Direct link to Usage")

Start the server `node index.js`

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](https://developers.telnyx.com/development/ngrok-setup) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings in the Mission Control Portal. To do this, click the edit symbol \[✎\] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

##### [Callback URLs For Telnyx Applications ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#callback-urls-for-telnyx-applications-2 "Direct link to Callback URLs For Telnyx Applications")

|     |     |
| --- | --- |
| Callback Type | URL |
| Inbound Message Callback | `{ngrok-url}/messaging/inbound` |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |

Once everything is setup, you should now be able to:

- Text your phone number and receive a response!
- Send a picture to your phone number and get that same picture right back!

## [.NET ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#net "Direct link to .NET")

⏱ **30 minutes build time**

### [Introduction ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#introduction-2 "Direct link to Introduction")

Telnyx's messaging API supports both MMS and SMS messsages. Inbound multimedia messaging (MMS) messages include an attachment link in the webhook. The link and corresponding media should be treated as ephemeral and you should save any important media to a media storage (such as AWS S3) of your own.

### [What you can do ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#what-you-can-do-2 "Direct link to What you can do")

At the end of this tutorial you'll have an application that:

- Receives an inbound message (SMS or MMS)
- Iterates over any media attachments and downloads the remote attachment locally
- Uploads the same attachment to AWS S3
- Sends the attachments back to the same phone number that originally sent the message

### [Pre-reqs & technologies ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#pre-reqs--technologies-2 "Direct link to Pre-reqs & technologies")

- Completed or familiar with the [Receiving SMS & MMS Quickstart](https://developers.telnyx.com/docs/messaging/messages/receive-message)
- A working [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS.
- Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/development/ngrok-setup))
- [DotNet Core](https://developers.telnyx.com/development/developer-setup#net) installed
- AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for more information.
- Previously created S3 bucket with public permissions available.

### [Setup ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-2 "Direct link to Setup")

#### [Telnyx Portal configuration ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#telnyx-portal-configuration-3 "Direct link to Telnyx Portal configuration")

Be sure to have a [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS and webhook URL pointing to your service (using ngrok or similar)

#### [Create a new dotnet core project ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#create-a-new-dotnet-core-project "Direct link to Create a new dotnet core project")

Create a new web project and set the output to `mms-demo`

```bash
$ dotnet new web -o mms-demo
$ cd mms-demo
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Install packages via dotnet CLI ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#install-packages-via-dotnet-cli "Direct link to Install packages via dotnet CLI")

```bash
$ dotnet add package AWSSDK.S3
$ dotnet add package dotenv.net
$ dotnet add package Telnyx.net
$ dotnet add package Microsoft.AspNetCore.Mvc.NewtonsoftJson
```

note

After pasting the above content, Kindly check and remove any new line added

This will add the requirements to the `.csproj` file with the packages needed to run the application.

#### [Setting environment variables ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setting-environment-variables-3 "Direct link to Setting environment variables")

The following environmental variables need to be set

|     |     |
| --- | --- |
| Variable | Description |
| `TELNYX_API_KEY` | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys) |
| `TELNYX_PUBLIC_KEY` | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key) |
| `TELNYX_APP_PORT` | **Defaults to `8000`** The port the app will be served |
| `AWS_PROFILE` | Your AWS profile as set in `~/.aws` |
| `AWS_REGION` | The region of your S3 bucket |
| `TELNYX_MMS_S3_BUCKET` | The name of the bucket to upload the media attachments |

#### [.env file ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#env-file-3 "Direct link to .env file")

This app uses the excellent [dotenv.net](https://github.com/bolorundurowb/dotenv.net) package to manage environment variables.

Make a copy of the file below, add your credentials, and save as `.env` in the root directory.

```bash
TELNYX_API_KEY=
TELNYX_PUBLIC_KEY=
TENYX_APP_PORT=8000
AWS_PROFILE=
AWS_REGION=
TELNYX_MMS_S3_BUCKET=
```

note

After pasting the above content, Kindly check and remove any new line added

### [Code-along ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#code-along-3 "Direct link to Code-along")

The `dotnet new web -o mms-demo` command scaffolds out a basic ASP.NET Core project structure with a few files and folders. We're focused mainly on:

- Program.cs
- Startup.cs

We'll also need a Controllers folder and a Controller to handle our webhooks from Telnyx.

```bash
$ mkdir Controllers
$ touch Controllers/TelnyxMessagingController.cs
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Modify Startup.cs to include controllers ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#modify-startupcs-to-include-controllers "Direct link to Modify Startup.cs to include controllers")

Update the `ConfigureServices` function to use the Controllers function and the NewtonsoftJSON library.

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddControllers().AddNewtonsoftJson();
}
```

note

After pasting the above content, Kindly check and remove any new line added

Update the `Configure` function to map the controllers. In the `app.UseEndpoints()` method add `endpoints.MapControllers();` so your `Configure` function looks like:

```csharp
public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    if (env.IsDevelopment())
    {
        app.UseDeveloperExceptionPage();
    }

    app.UseRouting();

    app.UseEndpoints(endpoints =>
    {
        endpoints.MapGet("/", async context =>
        {
            await context.Response.WriteAsync("Hello World!");
        });

      endpoints.MapControllers();

    });
}
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Modify Program.cs ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#modify-programcs "Direct link to Modify Program.cs")

Update the `Main` function to call the `DotEnv.Config();` function to load the values in the `.env` file to Environment variables.

- Be sure to add `using dotenv.net;`

```csharp
public static void Main(string[] args)
{
  DotEnv.Config();
  CreateHostBuilder(args).Build().Run();
}
```

note

After pasting the above content, Kindly check and remove any new line added

Update the `CreateHostBuilder` function to launch on the port as defined in the `.env` file:

```csharp
public static IHostBuilder CreateHostBuilder(string[] args) =>
    Host.CreateDefaultBuilder(args)
        .ConfigureWebHostDefaults(webBuilder =>
        {
            string Port = Environment.GetEnvironmentVariable("TELNYX_APP_PORT");
            webBuilder.UseStartup<Startup>();
            string[] urls = new string[] {$"http://localhost:{Port}", "https://localhost:8001"};
            webBuilder.UseUrls(urls);
        });
```

note

After pasting the above content, Kindly check and remove any new line added

### [Receiving Webhooks ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#receiving-webhooks-2 "Direct link to Receiving Webhooks")

Now that the basic app structure is setup, we need to create the Controller to receive webhooks for inbound messages & outbound message Delivery Receipts (DLR).

#### [TelnyxMessagingController.cs Scaffold ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#telnyxmessagingcontrollercs-scaffold "Direct link to TelnyxMessagingController.cs Scaffold")

Build out the controller to look something like the example below. The example includes all the packages the rest of the controller code will leverage.

```csharp
using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using System.IO;
using Newtonsoft.Json;
using System.Net.Http;
using System.Collections.Generic;
using Telnyx;
using Telnyx.net.Entities;
using Microsoft.AspNetCore.Http;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.S3.Transfer;
using Amazon;

namespace mms_demo.Controllers
{
  [ApiController]
  [Route("messaging/[controller]")]
  public class OutboundController : ControllerBase
  {
    // POST messaging/Inbound
    [HttpPost]
    [Consumes("application/json")]
    public async Task<string> MessageDLRCallback()
    {

    }
  }

  [ApiController]
  [Route("messaging/[controller]")]
  public class InboundController : ControllerBase
  {
    // POST messaging/Inbound
    [HttpPost]
    [Consumes("application/json")]
    public async Task<string> MessageInboundCallback()
    {

    }
  }
}
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Basic Routing & Functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#basic-routing--functions-3 "Direct link to Basic Routing & Functions")

The basic overview of the application is as follows:

1. Receive webhook & de-serialize JSON into a dynamic
2. Extract information from the webhook
3. Iterate over any media and download/re-upload to S3 for each attachment
4. Send the message back to the phone number from which it came
5. Acknowledge the status update (DLR) of the outbound message

#### [Webhook Helpers & Media Download/Upload Functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#webhook-helpers--media-downloadupload-functions "Direct link to Webhook Helpers & Media Download/Upload Functions")

Before diving into the inbound message handler, first we'll create a few functions within a new class `WebhookHelpers` to manage our attachments.

- `deserializeCallbackToDynamic` Reads JSON and returns a dynamic object.
- `UploadFileAsync` uploads the file passed to AWS S3 (and makes object public)
- `downloadMediaAsync` downloads the file to specified directory with the specified fileName

```csharp
public class WebhookHelpers
{
  public static async Task<dynamic> deserializeCallbackToDynamic(HttpRequest request){
    string json;
    using (var reader = new StreamReader(request.Body))
    {
      json = await reader.ReadToEndAsync();
    }
    dynamic webhook = JsonConvert.DeserializeObject<dynamic>(json);
    return webhook;
  }

  public static async Task<String> UploadFileAsync(string filePath)
  {
    string bucketName = System.Environment.GetEnvironmentVariable("TELNYX_MMS_S3_BUCKET");
    RegionEndpoint bucketRegion = RegionEndpoint.USEast2;
    IAmazonS3 s3Client = new AmazonS3Client(bucketRegion);
    TransferUtility fileTransferUtility = new TransferUtility(s3Client);
    string fileName = System.IO.Path.GetFileName(filePath);
    string mediaUrl = "";
    try
    {
      TransferUtilityUploadRequest fileTransferUtilityRequest = new TransferUtilityUploadRequest
      {
        BucketName = bucketName,
        FilePath = filePath,
        CannedACL = S3CannedACL.PublicRead
      };
      await fileTransferUtility.UploadAsync(fileTransferUtilityRequest);
      Console.WriteLine("Upload completed");
      mediaUrl = $"https://{bucketName}.s3.amazonaws.com/{fileName}";
    }
    catch (AmazonS3Exception e)
    {
      Console.WriteLine("Error encountered on server. Message:'{0}' when writing an object", e.Message);
    }
    catch (Exception e)
    {
      Console.WriteLine("Unknown encountered on server. Message:'{0}' when writing an object", e.Message);
    }
    return mediaUrl;
  }

  public static async Task<string> downloadMediaAsync(string directoryPath, string fileName, Uri uri)
  {
    HttpClient httpClient = new HttpClient();
    string uriWithoutQuery = uri.GetLeftPart(UriPartial.Path);
    string fileExtension = Path.GetExtension(uriWithoutQuery);
    string path = Path.Combine(directoryPath, $"{fileName}{fileExtension}");
    Directory.CreateDirectory(directoryPath);
    byte[] imageBytes = await httpClient.GetByteArrayAsync(uri);
    await File.WriteAllBytesAsync(path, imageBytes);
    return path;
  }
}
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Inbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#inbound-message-handling-4 "Direct link to Inbound message handling")

Now that we have the functions to manage the media, we can start receiving inbound MMS's

The flow of our function is (at a high level):

1. Extract relevant information from the webhook
2. Build the `webhook_url` to direct the DLR to a new endpoint
3. Iterate over any attachments/media and call our media management function
4. Send the outbound message back to the original sender with the media attachments

```csharp
[ApiController]
[Route("messaging/[controller]")]
public class InboundController : ControllerBase
{
  private string TELNYX_API_KEY = System.Environment.GetEnvironmentVariable("TELNYX_API_KEY");
  // POST messaging/Inbound
  [HttpPost]
  [Consumes("application/json")]
  public async Task<string> MessageInboundCallback()
  {
    dynamic webhook = await WebhookHelpers.deserializeCallbackToDynamic(this.Request);
    UriBuilder uriBuilder = new UriBuilder(Request.Scheme, Request.Host.ToString());
    uriBuilder.Path = "messaging/outbound";
    string dlrUri = uriBuilder.ToString();
    string to = webhook.data.payload.to[0].phone_number;
    string from = webhook.data.payload.from.phone_number;
    List<string> files = new List<string>();
    List<string> mediaUrls = new List<string>();
    if (webhook.data.payload.media != null)
    {
      foreach (var item in webhook.data.payload.media)
      {
        String url = item.url;
        Uri uri = new Uri(url);
        String fileName = item.hash_sha256;
        string path = await WebhookHelpers.downloadMediaAsync("./", fileName, uri);
        files.Add(path);
        string mediaUrl = await WebhookHelpers.UploadFileAsync(path);
        mediaUrls.Add(mediaUrl);
      }
    }
    TelnyxConfiguration.SetApiKey(TELNYX_API_KEY);
    MessagingSenderIdService service = new MessagingSenderIdService();
    NewMessagingSenderId options = new NewMessagingSenderId
    {
      From = to,
      To = from,
      Text = "Hello, World!",
      WebhookUrl = dlrUri,
      UseProfileWebhooks = false,
      MediaUrls = mediaUrls
    };
    MessagingSenderId messageResponse = await service.CreateAsync(options);
    Console.WriteLine($"Sent message with ID: {messageResponse.Id}");
    return "";
  }
}
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Outbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#outbound-message-handling-2 "Direct link to Outbound message handling")

As we defined our `webhook_url` path to be `/messaging/outbound` we'll need to create a function that accepts a POST request to that path within the controller.

```csharp
[ApiController]
[Route("messaging/[controller]")]
public class OutboundController : ControllerBase
{
  // POST messaging/Inbound
  [HttpPost]
  [Consumes("application/json")]
  public async Task<string> MessageDLRCallback()
  {
    dynamic webhook = await WebhookHelpers.deserializeCallbackToDynamic(this.Request);
    Console.WriteLine($"Received DLR for message with ID: {webhook.data.payload.id}");
    return "";
  }
}
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Final TelnyxMessagingController.cs ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#final-telnyxmessagingcontrollercs "Direct link to Final TelnyxMessagingController.cs")

All together the TelnyxMessagingController.cs should look something like:

```csharp
using System;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using System.IO;
using Newtonsoft.Json;
using System.Net.Http;
using System.Collections.Generic;
using Telnyx;
using Telnyx.net.Entities;
using Microsoft.AspNetCore.Http;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.S3.Transfer;
using Amazon;

namespace dotnet_starter.Controllers
{
  public class WebhookHelpers
  {
    public static async Task<dynamic> deserializeCallbackToDynamic(HttpRequest request){
      string json;
      using (var reader = new StreamReader(request.Body))
      {
        json = await reader.ReadToEndAsync();
      }
      dynamic webhook = JsonConvert.DeserializeObject<dynamic>(json);
      return webhook;
    }
    public static async Task<String> UploadFileAsync(string filePath)
    {
      string bucketName = System.Environment.GetEnvironmentVariable("TELNYX_MMS_S3_BUCKET");
      RegionEndpoint bucketRegion = RegionEndpoint.USEast2;
      IAmazonS3 s3Client = new AmazonS3Client(bucketRegion);
      TransferUtility fileTransferUtility = new TransferUtility(s3Client);
      string fileName = System.IO.Path.GetFileName(filePath);
      string mediaUrl = "";
      try
      {
        TransferUtilityUploadRequest fileTransferUtilityRequest = new TransferUtilityUploadRequest
        {
          BucketName = bucketName,
          FilePath = filePath,
          CannedACL = S3CannedACL.PublicRead
        };
        await fileTransferUtility.UploadAsync(fileTransferUtilityRequest);
        Console.WriteLine("Upload completed");
        mediaUrl = $"https://{bucketName}.s3.amazonaws.com/{fileName}";
      }
      catch (AmazonS3Exception e)
      {
        Console.WriteLine("Error encountered on server. Message:'{0}' when writing an object", e.Message);
      }
      catch (Exception e)
      {
        Console.WriteLine("Unknown encountered on server. Message:'{0}' when writing an object", e.Message);
      }
      return mediaUrl;
    }

    public static async Task<string> downloadMediaAsync(string directoryPath, string fileName, Uri uri)
    {
      HttpClient httpClient = new HttpClient();
      string uriWithoutQuery = uri.GetLeftPart(UriPartial.Path);
      string fileExtension = Path.GetExtension(uriWithoutQuery);
      string path = Path.Combine(directoryPath, $"{fileName}{fileExtension}");
      Directory.CreateDirectory(directoryPath);
      byte[] imageBytes = await httpClient.GetByteArrayAsync(uri);
      await File.WriteAllBytesAsync(path, imageBytes);
      return path;
    }
  }

  [ApiController]
  [Route("messaging/[controller]")]
  public class OutboundController : ControllerBase
  {
    // POST messaging/Inbound
    [HttpPost]
    [Consumes("application/json")]
    public async Task<string> MessageDLRCallback()
    {
      dynamic webhook = await WebhookHelpers.deserializeCallbackToDynamic(this.Request);
      Console.WriteLine($"Received DLR for message with ID: {webhook.data.payload.id}");
      return "";
    }
  }

  [ApiController]
  [Route("messaging/[controller]")]
  public class InboundController : ControllerBase
  {

    private string TELNYX_API_KEY = System.Environment.GetEnvironmentVariable("TELNYX_API_KEY");
    // POST messaging/Inbound
    [HttpPost]
    [Consumes("application/json")]
    public async Task<string> MessageInboundCallback()
    {
      dynamic webhook = await WebhookHelpers.deserializeCallbackToDynamic(this.Request);
      UriBuilder uriBuilder = new UriBuilder(Request.Scheme, Request.Host.ToString());
      uriBuilder.Path = "messaging/outbound";
      string dlrUri = uriBuilder.ToString();
      string to = webhook.data.payload.to[0].phone_number;
      string from = webhook.data.payload.from.phone_number;
      List<string> files = new List<string>();
      List<string> mediaUrls = new List<string>();
      if (webhook.data.payload.media != null)
      {
        foreach (var item in webhook.data.payload.media)
        {
          String url = item.url;
          Uri uri = new Uri(url);
          String fileName = item.hash_sha256;
          string path = await WebhookHelpers.downloadMediaAsync("./", fileName, uri);
          files.Add(path);
          string mediaUrl = await WebhookHelpers.UploadFileAsync(path);
          mediaUrls.Add(mediaUrl);
        }
      }
      TelnyxConfiguration.SetApiKey(TELNYX_API_KEY);
      MessagingSenderIdService service = new MessagingSenderIdService();
      NewMessagingSenderId options = new NewMessagingSenderId
      {
        From = to,
        To = from,
        Text = "Hello, World!",
        WebhookUrl = dlrUri,
        UseProfileWebhooks = false,
        MediaUrls = mediaUrls
      };
      MessagingSenderId messageResponse = await service.CreateAsync(options);
      Console.WriteLine($"Sent message with ID: {messageResponse.Id}");
      return "";
    }
  }
}
```

note

After pasting the above content, Kindly check and remove any new line added

### [Usage ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#usage-3 "Direct link to Usage")

Start the server:

```bash
$ dotnet restore
$ dotnet build
$ dotnet run
```

note

After pasting the above content, Kindly check and remove any new line added

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](https://developers.telnyx.com/development/ngrok-setup) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings in the Mission Control Portal. To do this, click the edit symbol \[✎\] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

##### [Callback URLs For Telnyx Applications ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#callback-urls-for-telnyx-applications-3 "Direct link to Callback URLs For Telnyx Applications")

|     |     |
| --- | --- |
| Callback Type | URL |
| Inbound Message Callback | `{ngrok-url}/messaging/inbound` |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |

Once everything is setup, you should now be able to:

- Text your phone number and receive a response!
- Send a picture to your phone number and get that same picture right back!

## [Ruby ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#ruby "Direct link to Ruby")

⏱ **30 minutes build time**

### [Introduction ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#introduction-3 "Direct link to Introduction")

Telnyx's messaging API supports both MMS and SMS messsages. Inbound multimedia messaging (MMS) messages include an attachment link in the webhook. The link and corresponding media should be treated as ephemeral and you should save any important media to a media storage (such as AWS S3) of your own.

### [What you can do ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#what-you-can-do-3 "Direct link to What you can do")

At the end of this tutorial you'll have an application that:

- Receives an inbound message (SMS or MMS)
- Iterates over any media attachments and downloads the remote attachment locally
- Uploads the same attachment to AWS S3
- Sends the attachments back to the same phone number that originally sent the message

### [Pre-reqs & technologies ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#pre-reqs--technologies-3 "Direct link to Pre-reqs & technologies")

- Completed or familiar with the [Receiving SMS & MMS Quickstart](https://developers.telnyx.com/docs/messaging/messages/receive-message#ruby)
- A working [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS.
- [Ruby & Gem](https://developers.telnyx.com/development/developer-setup#ruby) installed
- [Familiarity with Sinatra](https://sinatrarb.com/)
- Ability to receive webhooks (with something like [ngrok](https://developers.telnyx.com/development/ngrok-setup))
- AWS Account setup with proper profiles and groups with IAM for S3. See the [Quickstart](https://docs.aws.amazon.com/sdk-for-javascript/index.html) for more information.
- Previously created S3 bucket with public permissions available.

### [Setup ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-3 "Direct link to Setup")

#### [Telnyx portal configuration ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#telnyx-portal-configuration-4 "Direct link to Telnyx portal configuration")

Be sure to have a [Messaging Profile](https://portal.telnyx.com/#/app/messaging) with a phone number enabled for SMS & MMS and webhook URL pointing to your service (using ngrok or similar)

#### [Install packages via Gem/bundler ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#install-packages-via-gembundler "Direct link to Install packages via Gem/bundler")

```bash
gem install telnyx
gem install sinatra
gem install dotenv
gem install ostruct
gem install json
gem install aws-sdk
gem install down
```

note

After pasting the above content, Kindly check and remove any new line added

This will create `Gemfile` file with the packages needed to run the application.

#### [Setting environment variables ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setting-environment-variables-4 "Direct link to Setting environment variables")

The following environmental variables need to be set

|     |     |
| --- | --- |
| Variable | Description |
| `TELNYX_API_KEY` | Your [Telnyx API Key](https://portal.telnyx.com/#/app/api-keys) |
| `TELNYX_PUBLIC_KEY` | Your [Telnyx Public Key](https://portal.telnyx.com/#/app/account/public-key) |
| `TELNYX_APP_PORT` | **Defaults to `8000`** The port the app will be served |
| `AWS_PROFILE` | Your AWS profile as set in `~/.aws` |
| `AWS_REGION` | The region of your S3 bucket |
| `TELNYX_MMS_S3_BUCKET` | The name of the bucket to upload the media attachments |

#### [.env file ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#env-file-4 "Direct link to .env file")

This app uses the excellent [dotenv](https://github.com/bkeepers/dotenv) package to manage environment variables.

Make a copy of the file below, add your credentials, and save as `.env` in the root directory.

```bash
TELNYX_API_KEY=
TELNYX_PUBLIC_KEY=
TENYX_APP_PORT=8000
AWS_PROFILE=
AWS_REGION=
TELNYX_MMS_S3_BUCKET=
```

note

After pasting the above content, Kindly check and remove any new line added

### [Code-along ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#code-along-4 "Direct link to Code-along")

We'll use a singe `app.rb` file to build the MMS application.

```bash
touch app.rb
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Setup Sinatra Server ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#setup-sinatra-server "Direct link to Setup Sinatra Server")

```ruby
require 'sinatra'
require 'telnyx'
require 'dotenv/load'
require 'json'
require 'ostruct'
require 'aws-sdk-s3'
require 'down'

if __FILE__ == $0
  TELNYX_API_KEY=ENV.fetch("TELNYX_API_KEY")
  TELNYX_APP_PORT=ENV.fetch("TELNYX_APP_PORT")
  AWS_REGION = ENV.fetch("AWS_REGION")
  TELNYX_MMS_S3_BUCKET = ENV.fetch("TELNYX_MMS_S3_BUCKET")
  Telnyx.api_key = TELNYX_API_KEY
  set :port, TELNYX_APP_PORT
end

get '/' do
  "Hello World"
end
```

note

After pasting the above content, Kindly check and remove any new line added

### [Receiving Webhooks ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#receiving-webhooks-3 "Direct link to Receiving Webhooks")

Now that you have setup your auth token, phone number, and connection, you can begin to use the API Library to send/receive SMS & MMS messages. First, you will need to setup an endpoint to receive webhooks for inbound messages & outbound message Delivery Receipts (DLR).

#### [Basic routing & functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#basic-routing--functions-4 "Direct link to Basic routing & functions")

The basic overview of the application is as follows:

1. Verify webhook & create TelnyxEvent
2. Extract information from the webhook
3. Iterate over any media and download/re-upload to S3 for each attachment
4. Send the message back to the phone number from which it came
5. Acknowledge the status update (DLR) of the outbound message

#### [Media Download & Upload Functions ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#media-download--upload-functions-3 "Direct link to Media Download & Upload Functions")

Before diving into the inbound message handler, first we'll create a few functions to manage our attachments.

- `download_file` saves the content from a URL to disk
- `upload_file` uploads the file passed to AWS S3 (and makes object public)

```ruby
def upload_file(file_path)
  s3 = Aws::S3::Resource.new(region: AWS_REGION)
  name = File.basename(file_path)
  obj = s3.bucket(TELNYX_MMS_S3_BUCKET).object(name)
  obj.upload_file(file_path, acl: 'public-read')
  obj.public_url
end

def download_file(uri)
  temp_file = Down.download(uri)
  path = "./#{temp_file.original_filename}"
  FileUtils.mv(temp_file.path, path)
  path
end
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Inbound message handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#inbound-message-handling-5 "Direct link to Inbound message handling")

Now that we have the functions to manage the media, we can start receiving inbound MMS's

The flow of our function is (at a high level):

1. Extract relevant information from the webhook
2. Build the `webhook_url` to direct the DLR to a new endpoint
3. Iterate over any attachments/media and call our `download` & `upload` functions
4. Send the outbound message back to the original sender with the media attachments

```ruby
def deserialize_json(json)
  object = JSON.parse(json, object_class: OpenStruct)
  object
end

post '/messaging/inbound' do
  webhook = deserialize_json(request.body.read)
  dlr_uri = URI::HTTP.build(host: request.host, path: '/messaging/outbound')
  to_number = webhook.data.payload.to[0].phone_number
  from_number = webhook.data.payload.from.phone_number
  media = webhook.data.payload.media
  file_paths = []
  media_urls = []
  if media.any?
    media.each do |item|
      file_path = download_file(item.url)
      file_paths.push(file_path)
      media_url = upload_file(file_path)
      media_urls.push(media_url)
    end
  end

  begin
    telnyx_response = Telnyx::Message.create(
        from: to_number,
        to: from_number,
        text: "Hello, world!",
        media_urls: media_urls,
        use_profile_webhooks: false,
        webhook_url: dlr_uri.to_s
    )
    puts "Sent message with id: #{telnyx_response.id}"
  rescue Exception => ex
    puts ex
  end
end
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Outbound Message Handling ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#outbound-message-handling-3 "Direct link to Outbound Message Handling")

As we defined our `webhook_url` path to be `/messaging/outbound` we'll need to create a function that accepts a POST request to that path within messaging.js.

```ruby
post '/messaging/outbound' do
  webhook = deserialize_json(request.body.read)
  puts "Received message DLR with ID: #{webhook.data.payload.id}"
end
```

note

After pasting the above content, Kindly check and remove any new line added

#### [Final app.rb ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#final-apprb "Direct link to Final app.rb")

All together the app.rb should look something like:

```ruby
require 'sinatra'
require 'telnyx'
require 'dotenv/load'
require 'json'
require 'ostruct'
require 'aws-sdk-s3'
require 'down'

if __FILE__ == $0
  TELNYX_API_KEY=ENV.fetch("TELNYX_API_KEY")
  TELNYX_APP_PORT=ENV.fetch("TELNYX_APP_PORT")
  AWS_REGION = ENV.fetch("AWS_REGION")
  TELNYX_MMS_S3_BUCKET = ENV.fetch("TELNYX_MMS_S3_BUCKET")
  Telnyx.api_key = TELNYX_API_KEY
  set :port, TELNYX_APP_PORT
end

get '/' do
  "Hello World"
end

def deserialize_json(json)
  object = JSON.parse(json, object_class: OpenStruct)
  object
end

def upload_file(file_path)
  s3 = Aws::S3::Resource.new(region: AWS_REGION)
  name = File.basename(file_path)
  obj = s3.bucket(TELNYX_MMS_S3_BUCKET).object(name)
  obj.upload_file(file_path, acl: 'public-read')
  obj.public_url
end

def download_file(uri)
  temp_file = Down.download(uri)
  path = "./#{temp_file.original_filename}"
  FileUtils.mv(temp_file.path, path)
  path
end

post '/messaging/inbound' do
  webhook = deserialize_json(request.body.read)
  dlr_uri = URI::HTTP.build(host: request.host, path: '/messaging/outbound')
  to_number = webhook.data.payload.to[0].phone_number
  from_number = webhook.data.payload.from.phone_number
  media = webhook.data.payload.media
  file_paths = []
  media_urls = []
  if media.any?
    media.each do |item|
      file_path = download_file(item.url)
      file_paths.push(file_path)
      media_url = upload_file(file_path)
      media_urls.push(media_url)
    end
  end

  begin
    telnyx_response = Telnyx::Message.create(
        from: to_number,
        to: from_number,
        text: "Hello, world!",
        media_urls: media_urls,
        use_profile_webhooks: false,
        webhook_url: dlr_uri.to_s
    )
    puts "Sent message with id: #{telnyx_response.id}"
  rescue Exception => ex
    puts ex
  end
end

post '/messaging/outbound' do
  webhook = deserialize_json(request.body.read)
  puts "Received message DLR with ID: #{webhook.data.payload.id}"
end
```

note

After pasting the above content, Kindly check and remove any new line added

### [Usage ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#usage-4 "Direct link to Usage")

Start the server `ruby app.rb`

When you are able to run the server locally, the final step involves making your application accessible from the internet. So far, we've set up a local web server. This is typically not accessible from the public internet, making testing inbound requests to web applications difficult.

The best workaround is a tunneling service. They come with client software that runs on your computer and opens an outgoing permanent connection to a publicly available server in a data center. Then, they assign a public URL (typically on a random or custom subdomain) on that server to your account. The public server acts as a proxy that accepts incoming connections to your URL, forwards (tunnels) them through the already established connection and sends them to the local web server as if they originated from the same machine. The most popular tunneling tool is `ngrok`. Check out the [ngrok setup](https://developers.telnyx.com/development/ngrok-setup) walkthrough to set it up on your computer and start receiving webhooks from inbound messages to your newly created application.

Once you've set up `ngrok` or another tunneling service you can add the public proxy URL to your Inbound Settings in the Mission Control Portal. To do this, click the edit symbol \[✎\] next to your Messaging Profile. In the "Inbound Settings" > "Webhook URL" field, paste the forwarding address from ngrok into the Webhook URL field. Add `messaging/inbound` to the end of the URL to direct the request to the webhook endpoint in your server.

For now you'll leave “Failover URL” blank, but if you'd like to have Telnyx resend the webhook in the case where sending to the Webhook URL fails, you can specify an alternate address in this field.

##### [Callback URLs For Telnyx Applications ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms\#callback-urls-for-telnyx-applications-4 "Direct link to Callback URLs For Telnyx Applications")

|     |     |
| --- | --- |
| Callback Type | URL |
| Inbound Message Callback | `{ngrok-url}/messaging/inbound` |
| Outbound Message Status Callback | `{ngrok-url}/messaging/outbound` |

Once everything is setup, you should now be able to:

- Text your phone number and receive a response!
- Send a picture to your phone number and get that same picture right back!

On this page

- [Python ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#python)
- [PHP ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#php)
- [Node ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#node)
- [.NET ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#net)
- [Ruby ​](https://developers.telnyx.com/docs/messaging/messages/send-receive-mms#ruby)
