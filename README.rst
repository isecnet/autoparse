autoparse
=========

The goal is to process logs emitted from various applications and network components, 
and look for patterns that highlight a potential threat or need for further investigation.

The first step is to parse a wide variety of semi-structured logs. While a number of 
standard log formats exist, many are application specific and contain natural language 
messages that have relevant information. The time and cost to develop customer parsers 
is high, which is a constraining factor to mine additional potentially relevant sources
for information.

An automatic approach to parsing log records would open up the range of potentially 
relevant sources to identify threats.


General Approach
----------------

Firstly, logs from a variety of sources are parsed to extract entities and their relationships
into a graph representation. Logs consist of semi-structured documents (lines of text, JSON, XML,
or binary messages). A log document may have delimited fields and embedded free-form text. Using
NLP techniques may be of use. However, the grammar and syntax of log documents are probably not
as consistent as human language.

On the other hand, we can leverage the fact that logs consist of repeating templates (print
statements with interpolated variables).

We will therefore first extract these templates and variables using an algorithm called
Spell (Streaming Parser for Event Logs using Longest Common Subsequence), and a set of rules
to identify common entities such as IP Address, thus reducing the amount of work that NLP
techniques have to do as a secondary extraction step.

Once the relevant entities and relations have been inserted into the graph store, we will
apply various graph analytics and machine learning approaches to:

* Detect anomalies
* Identify communities (sub-graphs)
* Score and classify nodes, edges, or communities
* Predict relationships, e.g. to known indicators of compromise or attack


Run
---

Run the faust module

::

    # activate virtualenv, e.g. `pyenv activate autoparse`
    cd src
    export PYTHONPATH=.

    # 'main' refers to the `main.py` application file, starting a worker,
    # setting the log level to 'info'. A task in main reads logs from Arango.
    faust -A main worker -l info

You can see parsed logs published to Kafka using:

::

    kafka-console-consumer --topic parsed_logs --bootstrap-server localhost:9092 --property print.key=True

or

::

    kafka-console-consumer --topic parsed_logs --bootstrap-server localhost:9092 --property print.key=True --from-beginning

**Please note:**

The instructions below have been deprecated in favour of using Kafka and Faust as a
more reliable stream processing solution. (The shell-based pipes were breaking. A
queue-based approach is more suitable for the heavy processing performed.)

Modules support batch or stream mode. In stream mode, modules can be piped together

::

    # cd [Project Root Directory]
    export PYTHONPATH=src
    python src/read_from_es.py --stream | python src/parse.py --stream --log-format "<content>" 2>/dev/null | \
    python src/load.py --stream | python src/analyze.py --stream > /tmp/output.jsonl

or, as a convenience, using the provided bash scripts that include dependencies from
a virtualenv

::

    # cd [Project Root Directory]
    export PYTHONPATH=src
    ./scripts/read_from_es.sh -1 | ./scripts/parse.sh 2>/dev/null | \
    ./scripts/load.sh | ./scripts/analyze.sh > /tmp/output.jsonl

or trigger via a web service

::

    ./scripts/api.sh

    curl -X POST localhost:8000/logs

The above can also be deployed as a Docker container

::

    docker-compose up

    curl -X POST localhost:8000/logs

Environment variables must be configured in `.env` or `.env.docker` for the docker build.

The default output directory is `/tmp/cybersec/output`.

There is also a `NiFi <https://nifi.apache.org/>`_ template for setting up a stream-based
flow, under `src/nifi_templates`.

Alternatively, setup a streaming infrastructure such as Kafka Streams, `Faust <https://github.com/robinhood/faust>`_,
or equivalent.


Introduction
------------

Networks are monitored to detect threats and perform analysis once a potential threat is
identified. There are a number of challenges:

1. Network components and applications generate logs in various formats that must be parsed
   for analysis. Outside the standard log formats, there is a constant backlog of work to
   build parsers for new logs.
2. In addition, the parsers generally extract structured information but leave behind relevant
   information in text fields.
3. The extracted entities (and relations) form a natural graph. It would be useful to create
   a graph that can be queries and linked to various external sources such as malware databases,
   blacklisted IP addresses, and so on.

We can use the graph structure to make predictions and perform inference. For example, there
has been recent research using a graph as input to a recurrent neural network (e.g. an LSTM).

Our initial task is:

1. A mechanism to extract entities into a graph representation. The entity types are defined
   in a UDM (Unified Data Model).
2. Data engineering is required to get access to required data and process it in a repeatable
   and automated manner consistent with whatever standards have already been put in the place
   for the project - or help define suitable standards.


High-level Process Flow
-----------------------

1. Read logs from Elasticsearch and publish as a stream.

   1b. (Option) Use Sigma to extract log records of interest from Elasticsearch using rules
       that look for potential threats

2. Parse stream using rules (e.g. regular expressions) and NLP named entity recognition (currently
   using Spacy's out-of-the-box 'en_core_web_sm' model) to identify entities such as an IP address
   in a log line.

3. Process log lines using Spell to identify log keys (a recurring text pattern once you remove
   parameters, either identified in step 2) or from the Spell algorithm as the changing part
   of an otherwise static pattern.

   3b. Anomaly detection given features extracted from logs parsed using Spell

4. Process log keys using NLP (e.g. named entity recognition) to identify any additional entities
   or relations

5. Write entities and relations to the graph database (ArangoDB)

6. Query the graph database for relevant analytics

The main challenge with applying machine learning to the graph data is availability of relevant
labelled datasets. Most approaches use supervised learning which requires data examples to learn
from.

The following initial machine learning models have been developed:

1. `Malicious URL Detector <src/ml/url_classifier/>`_ (Supervised)

2. `Node2vec Clustering <src/ml/node2vec/>`_ (Unsupervised)


Documentation
-------------

1. `Design <docs/design.rst>`_

2. `Process <docs/process.rst>`_

3. `Extracting message types from logs <docs/extracting_message_types.rst>`_

4. `Spell (Streaming Parser for Event Logs using Longest Common Subsequence) <docs/spell.rst>`_

5. `Knowledge Graph <docs/knowledge_graph.rst>`_

6. `Ontology <docs/ontology.rst>`_

7. `Intro to the domain <docs/domain_basics.rst>`_

8. `Security Information and Event Management (SIEM) information <docs/siem.rst>`_

9. `Setup a test environment <docs/setup.rst>`_

10. `Data Sources <docs/data_sources.rst>`_
