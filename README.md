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

- Robocorp Control Room account (sign up for free)
- Timescale account with a deployment (free trials available)
- OpenAI API key
- *(Recommended)* Robocorp Code extension for VS Code, connecting your IDE to Control Room for easier local development (download for free)

**TODO**