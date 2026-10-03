---
title: "Workflow Engines: Why So Many?"
---

# Workflow Engines: Why So Many?

<div class="wiki-archive-note" markdown="span">Archived from the ESIP wiki page <a href="https://wiki.esipfed.org/Workflow_Engines:_Why_So_Many?">Workflow Engines: Why So Many?</a>.</div>

Part of the
[ESIP Information Technology and Interoperability 2010 Rants and Raves
Webinar Series](2010-rant-and-raves-webinar-series-and-telecon-information.md).

Presented on Wednesday, April 7, 2010 at 11:00am PST.

## Abstract

Workflow engines are becoming more commonly used in Earth Science data
systems. But the with plethora of workflow engines to choose from and
the variability of their capabilities, it may be time consuming to
assess which workflow engine is best suited for a particular domain
adaptation. We will explore the diverse capabilities of a few selected
workflow engines and discuss some of the relevant capabilities useful
for Earth Science data systems.

## Presentation

Slides:
[esip_iti_webinar_workflow_engines_why_so_many.pdf](files/Esip_iti_webinar_workflow_engines_why_so_many.pdf)

## Discussion

- **Interoperability among workflow engines.** Can mitigate
  interoperability risks by leveraging more standards-oriented
  constructs. For example, in distributed workflows, wrap components as
  simple REST/SOAP service endpoints. This maximizes the ability to swap
  the workflow engines without modifying the service components. The
  invocation essentially remains unchanged. Also, many of the workflow
  engines are BPEL-based so variations across implementations are not as
  dramatic. Currently, some workflow engines are adhering to the [OASIS
  WS-BPEL 2.0
  spec](http://docs.oasis-open.org/wsbpel/2.0/OS/wsbpel-v2.0-OS.html).
- **How does an organization develop strategy to marshaling or
  streamline the rapid proliferation of workflows (into fewer/faster
  workflows)?** One approach is to leverage more of workflow reuse
  through appropriate abstraction layers of nested workflows. Another
  approach is to take a more collaborative view and share workflows in a
  community. An example is [myExperiment](http://www.myexperiment.org/),
  which "makes it easy to find, use and share scientific workflows and
  other Research Objects, and to build communities."

## References

**Workflow Engines**

- [Apache  ODE](http://ode.apache.org/)
- [JBoss jBPM](http://www.jboss.org/jbpm)
- [Workpoint: PBM with Torque](http://www.workpoint.com/)
- [Flux](http://fluxcorp.com/)
- [GeoBrain BPELPower Workflow
  Engine](https://wiki.esipfed.org/GeoBrain_BPELPower_Workflow_Engine)
- [GeoBrain Online Analysis System
  (GeOnAS)](http://geobrain.laits.gmu.edu:81/OnAS)
- [Multi-mission Automated Task Invocation
  System](http://www.techbriefs.com/component/content/article/5893)
- [Taverna Workbench](http://www.taverna.org.uk/)
- [VisTrails](http://www.vistrails.org/)
- [SciFlo](http://sciflo.jpl.nasa.gov/)
- [PHX
  ModelCenter](http://www.phoenix-int.com/software/phx_modelcenter.php)
- [Kepler](https://kepler-project.org/)
- [Talkoot](http://miningsolutionsdev.itsc.uah.edu/talkoot/)

**Papers**

- [Sebastian  Bergmann, "Design and Implementation of a Workflow
  Engine", IAI‐TR‐2007‐5,  September 
  2007](http://sebastian-bergmann.de/publications/bergmann-WorkflowEngine-DiplomaThesis.pdf)

**Misc**

- [BeanShell: Lightweight Scripting for Java](http://www.beanshell.org/)
- [myExperiment](http://www.myexperiment.org/)
- [Data-type and Service
  Ontologies](https://wiki.esipfed.org/Data_Service_Ontologies)
- [OASIS WS-BPEL
  2.0](http://docs.oasis-open.org/wsbpel/2.0/OS/wsbpel-v2.0-OS.html)

------------------------------------------------------------------------

Hook Hua 2010-04-08T23:05:00-07:00
