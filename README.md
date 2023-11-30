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

[ADD SCREENSHOT]

2. Create two [Robocorp Vault](https://robocorp.com/docs/development-guide/variables-and-secrets/vault) items that house your secrets:
  - One called `OpenAI` that has one entry called `key` that contains your OpenAI API key.
  - Second called `Timescale` that has your Timescale service url in an entry called `service-url`.

You'll find the Service URL from your Timescale console under Connection Info, here:

[ADD SCREENSHOT]

## Raw Python to Robocorp Task

In the example code this is already done, but considering you'd start from a "plain vanilla" Python script, this is what you'd do.

### 1. Set up your dependencies in the [conda.yaml](conda.yaml) file and declare the runnables

Generally this is simple, you just move all you normally `pip install` under the pip dependencies in the configuration file. Why? The reason is that the runtimes will build the Python environment according to these specs. On your machine, and later where ever the Task gets executed. This is really the secret ingredient here. You'll not be on the mercy of what ever Python versions the runtime has, as Robocorp always runs Tasks in it's fully isolated and replicable environment.

In this case there is a small trick needed.

```yaml
dependencies:
  - python=3.10.12                # https://pyreadiness.org/3.10
  - pip=23.2.1                    # https://pip.pypa.io/en/stable/news
  - robocorp-truststore=0.8.0     # https://pypi.org/project/robocorp-truststore/
  - psycopg2=2.9.7                # https://pypi.org/project/psycopg2/
  - pip:
    - robocorp==1.2.4             # https://pypi.org/project/robocorp
    - robocorp-browser==2.2.1     # https://pypi.org/project/robocorp-browser
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

### Wrap your code in a `@task`

```python
from robocorp.tasks import task

@task
def my_timescale_loader():
    # All the things you wanna do
```

