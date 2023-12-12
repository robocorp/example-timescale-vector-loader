# Production-ready RAG data loaders feat. Timescale Vector and Llamaindex

You've got your amazing RAG AI app ready. You've got the data loaders done, but they run on your laptop. Now what? Where to run them on schedule or otherwise repeatable? Or even make other people able to use them? You've come to the right place!

**This tutorial shows how to run production-grade RAG data loaders on Robocorp.**

With Robocorp, you can run Python on a scale anywhere. It comes with built-in logging, a powerful orchestrator with an API to everything, and scalable runtimes in the cloud or on-prem. In this case, we are focusing on these highlights:

- How to wrap your RAG data loader to a runnable Robocorp Task and instantly get detailed logs of every execution
- How to schedule a Task to run on the Robocorp Control Room using on-demand containers
- How to send an email to your RAG loader to process the attachments - *with zero additional lines of code*

The video below will show you some of the cool highlights.

[![intro-video](https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/2ac6ca36-869a-44c2-ae24-641e1c06728d)](https://www.youtube.com/watch?v=1ExyKcF5jP4)

Let's get going!

## What you'll need

To complete this tutorial yourself, you'll need the following:

- Robocorp Control Room account ([sign up for free](https://cloud.robocorp.com/))
- Timescale account with a deployment ([free trials available]())
- OpenAI API key
- Robocorp Code extension for VS Code, connecting your IDE to Control Room for easier local development ([download for free](https://marketplace.visualstudio.com/items?itemName=robocorp.robocorp-code))

Once all is installed, do the following (if you follow the names exactly, the code will work without changes):

1. Link your development environment to the Robocorp Cloud and your workspace.

<img width="535" alt="robocorp-code" src="https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/c74cc0b6-b212-46d8-a1e1-de131171518a">

2. Create two [Robocorp Vault](https://robocorp.com/docs/development-guide/variables-and-secrets/vault) items that house your secrets:
  - One called `OpenAI` that has one entry called `key` that contains your OpenAI API key.
  - Second called `Timescale` that has your Timescale service URL in an entry called `service-url`.

You'll find the Service URL from your Timescale console under Connection Info here:

![timescale-console](https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/13d84c94-e1da-45fe-95d5-a8aae6707b3d)

## Raw Python to Robocorp Task

In the example code, this is already done, but considering you'd start from a "plain vanilla" Python script, this is what you'd do.

### 1. Set up your dependencies in the [conda.yaml](conda.yaml) file and declare runnables

Generally, this is simple; you move all your normal `pip install`s under the pip dependencies in the configuration file. Why? The reason is that the runtimes will build the Python environment according to these specs. On your machine and later wherever the Task gets executed. This is the secret ingredient here. You'll not be at the mercy of whatever Python versions the runtime has, as Robocorp always runs Tasks in its fully isolated and replicable environment.

In this case, a small trick is needed.

```yaml
dependencies:
  - python=3.10.12
  - pip=23.2.1
  - robocorp-truststore=0.8.0
  - psycopg2=2.9.7
  - pip:
    - robocorp==1.2.4
    - timescale-vector==0.0.3
    - openai==1.3.5
    - llama-index==0.9.7
    - psycopg2-binary==2.9.9
    - pypdf==3.17.1
```

For the Timescale connection to work, you'll need to have the `psycopg2` package coming from the conda-forge (top-level item) and also add `psycopg2-binary`, but that needs to come from pip.

Next, you'll make sure that your [robot.yaml](robot.yaml) contains the declarations of what the Control Room can see as runnables. In this case, you would see `Data Loader` and `Do a Query` Tasks in your workspace.

```yaml
tasks:
  Data Loader:
    shell: python -m robocorp.tasks run tasks.py -t my_timescale_loader
  Do a Query:
    shell: python -m robocorp.tasks run tasks.py -t query_from_vectordb
```

### 2. Wrap your code in a `@task`

The next step is wrapping your existing code in a method and adding a `@task` decorator. It does a bunch of things, for example automatically initializes the intricate logging that Robocorp provides, as well as enables you to run the code easily using the environment just configured in the previous step.

This is what you'll be adding, and all your code goes into the middle where the comment is:

```python
from robocorp.tasks import task

@task
def my_timescale_loader():
    # All the things you wanna do
```

### 3. Hide the secrets

As we will run the code somewhere other than on your own laptop (for example, on-demand cloud runtimes), we can't rely on your local environment variables anymore. In the example code, we've wrapped all the necessary setup steps in a method, which pulls the necessary credentials from the Robocorp Vault and sets the necessary (environment) variables. Like this:

```python
def setup():
    # Set up all the credentials from Robocorp Vault
    openai_credentials = vault.get_secret("OpenAI")
    os.environ["OPENAI_API_KEY"] = openai_credentials["key"]
    timescale_credentials = vault.get_secret("Timescale")
    return timescale_credentials["service-url"]
```

### 4. Use the Work Items

Last but not least, we'll put Work Items into work.

Our code builds the embeddings from a local folder, `data`, so we must get some stuff into that folder first. The easiest way is to use work items, which can contain JSON payloads or files. Now, we are only interested in files. The fancy part of Robocorp Control Room is that regardless of how the Task gets triggered, it'll pass the files in as input Work Items. So you could call the Task with an API with files, you can send an email with attachments, or manually start a run with files from the Control Room. In all cases, just these two lines will do the trick.

```python
for input in workitems.inputs:
    input.get_files("*", "data")
```

They'll iterate through all the available Work Items, and save all files to the local `data` folder.

Now you are good to go!

## Running it locally

The tutorial repository contains three example Work Items for easy testing:

- [simple-file](devdata/work-items-in/simple-file/work-items.json) is just one input `.txt` file
- [multiple-files](devdata/work-items-in/multiple-files/work-items.json) contains two pdf files
- [email](devdata/work-items-in/email/work-items.json) contains an example of how the email is represented as a Work Item when sent to the Control Room to trigger the run

To run and debug locally in VS Code, the easiest way is through Command Palette (CTRL + Shift + P or Command + Shift + P) and Robocorp: Run Robot. That way, the run happens in the environment you have defined.

You'll be prompted for two things.

First, which Task to run? The repo contains two: `Data Loader` is where the beef is. `Do a Query` is there to validate if your data loader worked. It creates a simple query engine and runs one query against your database.

Second, choose the input Work Item. For the `Data Loader`, try any of the three available. Or jump to the deep end and create your own test Work Items from the Resources panel in the Robocorp Code extension. For the `Do a Query` task, you don't need any work item.

After running something locally, check the Robo Task Output to see what the run did. If anything failed, it's easy to see what went south.

<img width="1411" alt="logs" src="https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/a87f5ea5-cc03-4d78-95e9-56c5fc4a7de2">

## Going cloud ☁️

Now that all runs locally, time to go production-grade. In this section we'll do the following things: upload the project to the Control Room, create a process out of it, set up an email trigger and test it.

### 1. Deploy code to Control Room

While you can upload your project directly from VS Code to the Control Room (Command Palette - Robocorp: Upload Robot to the Control Room), the recommended way is to do it via the git repo. You may fork this repo to your own, or simply just use our example repo directly.

It's easy: Tasks tab under your Workspace, Add Task Package, give it a name, and paste the link to the repo. Done.

![create-tasks](https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/95cf3b7f-6604-4f68-8455-bbef780ce954)

### 2. Create a Process

Next up, you'll need to create a Process. Tasks are reusable components that you can use to build sequences of actions. When creating a Process you'll map your chosen Tasks with the Worker runtimes.

Follow the UI again, as the video below shows. Processes, Create a new Process and add your details.

Once that's done, you'll have an opportunity to either set the scheduling, or create an email trigger. We'll choose the latter. In the last step, you can create alerts and callbacks to Slack, Email and as Webhook calls. In this example we set a Slack notification for both successfull and unsuccessful runs.

![create-process](https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/32a67f01-05c6-4065-a6de-e67fe3a86e92)

### 3. Run it manually

Once the Proces is created, time to run it! Hit the Run Process button and choose Run with Input Data, and give a file as an input. Once the run is complete, your Timescale has embeddings in it! 🤞

<img width="1279" alt="run-process" src="https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/fecb6904-4f5e-427a-aa72-140044bb7f00">

**Tip:** open the Process run for detailed log on the execution.

### 4. Start with email

Pushing this even further, next grab the email address of the process, you'll find it from the Configuration of the Process under Scheduling.

![email-trigger](https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/a1759229-4639-4022-8700-e7a0466ddef1)

Now what ever you send to that particular email automatically triggers your run, takes the attachments as input files and loads them to your vector database. And remember: you did not write a single line of code that handles emails! ✨ We did it for you.

## Push the boundaries

Now when all the basics work, here are some ideas of what else you could do with Robocorp!

- Build more complex data loaders that e.g. get data from websites and runs on a daily schedule. Here's a [repo](https://robocorp.com/portal/robot/robocorp/example-langchain-data-ingestion) for inspiration.
- Deploy self-hosted workers so that the data loader has access to data and systems inside your own network.
- Each Process is callable over Control Room API. Try triggering the load process with an API call.
