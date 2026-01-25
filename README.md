# [DHTI Elixirs](https://github.com/dermatologist/dhti)

<p align="center">
  <img src="https://github.com/dermatologist/dhti/blob/develop/notes/dhti-logo.jpg" />
</p>

- 🚀 *What might healing become if we dared to distill possibility itself!*

## Overview
Elixirs are modular Langserve healthcare apps following health data standards and best practices such as **FHIR and CDS-Hooks**. This is a monorepo of elixirs for [DHTI](https://github.com/dermatologist/dhti).

[DHTI](https://github.com/dermatologist/dhti) provides command-line tools (`dhti-cli`) for installation and management of DHTI elixirs using docker containers. [DHTI](https://github.com/dermatologist/dhti) [Vidhis](https://github.com/dermatologist/dhti/blob/develop/vidhi/README.md) (receipes) provides a set of shell commands that you can used to easily spin up a complete DHTI environment with modules such as the *Chatbot Agent (with patient chart context), RAG, Imaging Report widget, Orthanc DICOM viewer,* and more. Additionally, there is a browser extension that allows you to capture webpage content and send it to the DHTI elixir.

**The best way to start using these microfrontends is by following the [DHTI Vidhis](https://github.com/dermatologist/dhti/blob/develop/vidhi/README.md).** Also see the [![Wiki](https://img.shields.io/badge/DHTI-wiki-demo)](https://github.com/dermatologist/dhti/wiki). Individual packages also have their own README files with more details.

[How to contribute elixirs?](CONTRIBUTING.md)

## Starting with dhti (Example)

```bash

npx dhti-cli elixir install -g https://github.com/dermatologist/dhti-elixir.git -n dhti-elixir-schat -s packages/simple_chat

```

## Available Elixirs

- [DHTI Simple Chat Elixir](packages/simple_chat/README.md): A simple chat interface for DHTI using LLMs.
- [DHTI Agent Chat Elixir](packages/agent_chat/README.md): An agent-based chat interface for DHTI using LLMs.
- [DHTI Imaging Report Elixir](packages/imaging_report/README.md): A vision-capable elixir for analyzing medical images and generating reports using multimodal AI models.
- [File Uploader Elixir](packages/upload_file/README.md): An elixir to upload files to vectorstore.
- [DHTI Simple RAG Elixir](packages/simple_rag/README.md): A simple RAG elixir that reads from vectorstore.

## Repository Structure

```
├── packages/
│   ├── agent_chat/
│   │   ├── pyproject.toml
│   │   └── src/dhti_elixir_achat/
│   │       ├── __init__.py
│   │       ├── bootstrap.py
│   │       ├── chain.py
│   │       └── server.py
│   ├── simple_chat/
│   │   ├── pyproject.toml
│   │   └── src/dhti_elixir_schat/
│   │       ├── __init__.py
│   │       ├── bootstrap.py
│   │       ├── chain.py
│   │       └── server.py
│   ├── simple_rag/
│   │   └── src/dhti_elixir_srag/
│   ├── imaging_report/
│   │   └── src/dhti_elixir_imaging_report/
│   ├── starter/
│   │   └── src/dhti_elixir_starter/
│   └── upload_file/
│       └── src/dhti_elixir_upload/
├── docs/
│   ├── index.md
│   ├── modules.md
│   └── contributing.md
├── tests/
│   ├── agent_chat/
│   ├── imaging_report/
│   ├── simple_chat/
│   └── simple_rag/
├── README.md
├── pyproject.toml
└── (other configs: Dockerfile, Makefile, .github/, .vscode/)
```



## Give us a star ⭐️
If you find this project useful, give us a star. It helps others discover the project.


## Contributing

Please see the [Contributing Guide](CONTRIBUTING.md) for information about contributing to this project.

## Contributors

* [Bell Eapen](https://nuchange.ca) ([UIS](https://www.uis.edu/directory/bell-punneliparambil-eapen)) |  [Contact](https://nuchange.ca/contact) | [![Twitter Follow](https://img.shields.io/twitter/follow/beapen?style=social)](https://twitter.com/beapen)