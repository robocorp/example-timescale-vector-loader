# Production-ready RAG data loaders feat. Timescale Vector and Llamaindex

You've got your amazing RAG AI app ready. You've got the data loaders done, but they run on your laptop. Where to run them on schedule or otherwise repeatable? Or even make other people able to use them? You've come to the right place!

**This tutorial focuses on showing how to run production-grade RAG data loaders on Robocorp.**

With Robocorp, you can run Python on scale anywhere. It comes with built-in logging, powerful orchestrator with an API to everything, and scalable runtimes in cloud or on-prem. In this case, we are focusing on these highlights:

- How to wrap your RAG data loader to a runnable Robocorp Task, and instantly get detailed logs of every execution
- How to schedule a Task to run on Robocorp Control Room using on-demand containers
- How to send an email to your RAG loader to process the attachments - *with zero additional lines of code*

Let's get going!

## What you'll need

In order to complete this tutorial yourself, you'll need the following:

- Robocorp Control Room account ([sign up for free](https://cloud.robocorp.com/))
- Timescale account with a deployment ([free trials available]())
- OpenAI API key
- Robocorp Code extension for VS Code, connecting your IDE to Control Room for easier local development ([download for free](https://marketplace.visualstudio.com/items?itemName=robocorp.robocorp-code))

Once all is installed do the following (if you follow the names exactly, the code will work without changes):

1. Link your development environment to the Robocorp Cloud and your workspace.

<img width="535" alt="robocorp-code" src="https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/c74cc0b6-b212-46d8-a1e1-de131171518a">

2. Create two [Robocorp Vault](https://robocorp.com/docs/development-guide/variables-and-secrets/vault) items that house your secrets:
  - One called `OpenAI` that has one entry called `key` that contains your OpenAI API key.
  - Second called `Timescale` that has your Timescale service url in an entry called `service-url`.

You'll find the Service URL from your Timescale console under Connection Info, here:

![timescale-console](https://github.com/robocorp/example-timescale-vector-loader/assets/40179958/13d84c94-e1da-45fe-95d5-a8aae6707b3d)

## Raw Python to Robocorp Task

In the example code this is already done, but considering you'd start from a "plain vanilla" Python script, this is what you'd do.

### 1. Set up your dependencies in the [conda.yaml](conda.yaml) file and declare the runnables

Generally this is simple, you just move all you normally `pip install` under the pip dependencies in the configuration file. Why? The reason is that the runtimes will build the Python environment according to these specs. On your machine, and later where ever the Task gets executed. This is really the secret ingredient here. You'll not be on the mercy of what ever Python versions the runtime has, as Robocorp always runs Tasks in it's fully isolated and replicable environment.

In this case there is a small trick needed.

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

In order for the Timescale connection to work, you'll need to have the `psycopg2` package coming from the conda-forge (top level item), and also add `psycopg2-binary`, but that needs to come from pip.

Next, you'll make sure that your [robot.yaml](robot.yaml) contains the declarations of what Control Room can see as runnables. In this case you would see `Data Loader` and `Do a Query` Tasks show up in your workspace.

```yaml
tasks:
  Data Loader:
    shell: python -m robocorp.tasks run tasks.py -t my_timescale_loader
  Do a Query:
    shell: python -m robocorp.tasks run tasks.py -t query_from_vectordb
```

### 2. Wrap your code in a `@task`

Next step is wrapping your existing code in a method, and add a `@task` decorator. It does bunch of things, for example automatically initializes the intricate logging that Robocorp provides, as well as enable you to run the code easily using the environment just configured in the previous step.

This is what'll you be adding, and all your code goes in to the middle where the comment is:

```python
from robocorp.tasks import task

@task
def my_timescale_loader():
    # All the things you wanna do
```

### 3. Hide the secrets

As we are going to run the code somewhere else than on your own laptop (for example on-demand cloud runtimes), we can't rely on your local environment variables anymore. In the example code we've wrapped all the necessary setup steps in a method, which pulls the necessary credentials from the Robocorp Vault, and sets the necessary (environment) variables. Like this:

```python
def setup():
    # Set up all the credentials from Robocorp Vault
    openai_credentials = vault.get_secret("OpenAI")
    os.environ["OPENAI_API_KEY"] = openai_credentials["key"]
    timescale_credentials = vault.get_secret("Timescale")
    return timescale_credentials["service-url"]
```

### 4. Use the Work Items

Last but not least, we'll put Work Items in to work.

Our code builds the embeddings from a local folder `data`, so we need to get some stuff in to that folder first. The easiest way is to use work items, which can contain JSON payloads or files. Now we only are interested in files. The fancy part of Robocorp Control Room is that regardless of the way the Task gets triggered, it'll pass the files in as input Work Items. So you could call the Task with an API with files, you can send and email with attachments, or manually start a run with files from the Control Room. In all cases, just these two lines will do the trick.

```python
for input in workitems.inputs:
    input.get_files("*", "data")
```

They'll iterate through all the available Work Items, and save all files to the local `data` folder.

Now you are good to go!

## Running it locally

The tutorial repository contains three example Work Items for easy testing:

- [simple-file](devdata/work-items-in/simple-file/work-items.json) is just one input txt file
- [multiple-files](devdata/work-items-in/multiple-files/work-items.json) contains two pdf files
- [email](devdata/work-items-in/email/work-items.json) contains an example of how the email is represented as a Work Item, when sent to Control Room to trigger the run

To run and debug locally in VS Code, the easiest way is through Command Palette (CTRL + Shift + P or Command + Shift + P) and Robocorp: Run Robot. That way the run happens in the environment you have defined.

You'll be prompted for two things.

First, which Task to run. The repo contains two: `Data Loader` is where the beef is. `Do a Query` is there to validate if your data loader actually worked. It creates a simple query engine and runs one query against your database.

Second, choose the input Work Item. For the `Data Loader`, try any of the three available. Or go advanced and create your own test Work Items from the Resources panel in Robocorp Code extension. For the `Do a Query` task, you don't need any work item.

After running something locally, check the Robo Task Output to see what the run did. If anything failed, it's easy to see what went south.

[image here]

## Going cloud

Now that all runs locally, time to go production-grade and put Robocorp properly work. In this section we'll do the following things: upload the project to the Control Room, create a process out of it, set up an email trigger and test it.

### 1. Deploy code to Control Room

While you can upload your project directly from VS Code to the Control Room (Command Palette - Robocorp: Upload Robot to the Control Rom), the recommended way is to do it via the git repo. You may fork this repo to your own, or simply just use our example repo directly.

