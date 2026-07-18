in this session we need to come up with a solution on the architecture of 'groves' marketplace/inheritance/plug-in.

With time it became clear that the orchestrator
the groves (under groves/ directory)
and orchestration infrastructure (everything else, not under groves/ directory)
shall belong to separate logical units. Hence, groves for convenience of sharing and inheriting shall be distributed as
separate repositories.

# Grove inheritance
Grove becomes a building block and something like a base class (and most certainly some implementation of a base class).
If we look into the way the groves/..../spanish/context.md is organized - we can see that it points to rioplatense anki deck
specification that inherits and builds on top of a more generic 'languages'.

I presume not all groves will use anki-mcp. We need to consider which functions deserve to be in the diotima orchestrator and which
have to be enable for groves. What will be in 'base grove' repository


# Forward compatibility
now there is Anki integration, but there will be other systems so we need forward compatibility with those.
Video extraction with youtube-extract skills is one of such examples
skills/youtube-extract/extract.py:41 relies on focus-area.md file

Since we have a lot of considerations about inheritence and well defined structure, maybe it would make sense to
consider making groves more deterministic altogether. Now they are pure semantic llm navigation driven.
I'm considering maybe interacting with some parts of groves could be jupyter notebook...
But again, the grove repository is for the most part is a normal repository and people can make whatever they want there,
they can make some base class grove with jupyter support of some process and those repositories who are based on this
'jupyter-support' repo - can benefit from it.
What will be the mechanics I decide to include some nice feature to the core diotima runtime?
Do we even need a diotima runtime?

# Scope - how abstract do we want to go?
I presume if we don't impose some limitations and want to make absolute abstraction - we are back to github submodules, so there
needs to be something useful.
On the other hand, not making it abstract enough strips me from the opportunity of a completely diferent caliber...

High level paradigm shift - humans start sharing directories as content not as a tool or means.
Just like people share links to youtube videos.
So apparently the fundamental tool that is required in a runtime engine is mem-bank. Especially because it is without RAG and
thus no technical knowledge is required to review it's full state. It forces people to think what they talk about with their grove
repository.
Grove repository doesn't have to only be used for learning but people can share them as their personal blogs. The benefit is that
their path is summarized and filtered so they get a blog in the cheapest possible way, just going about their business while the
memory bank taking notes automatically.

Here I'm not sure whether I'm not shooting too high.

Provide me with potential variants and help me to brainstorm

Do the grove have to be the basic minimal atom of the infrastructure like a Java object or we need some other which I'm mostly thinking about another primitive below that will have no tooling and no capability besides ensuring that improvement to actual groves can be forward propagated somehow or can be propagated some purely infrastructural thing insuring that or stating or providing the intention of saying that we are having repositories and repository is the object and we are composing repositories in to inheritance so basically we have inheritance of repositories
One of the things for example that we might want to fall or to propagate to existing for example the situation that I'm thinking about is let's say we have already some groves defined and let's say let's say for now groves only support memory and they support the memory bank but one day I decide I want them to be able to host opencode skills and I want to give support for skills for example so that people can define skill there and the skills will be somehow red or processed or by the by the infrastructure

Also consider whether this my project initiative will not be one day just replaced by a small feature drop of a giant like Gemini or others like notebookLM

Consider forking a base repository versus actually creating a new repository for every iteration of inheritance for every basically I'm thinking when base class is a repository and derived class is a completely different repository that has a base class as a submodule or derived repository is a fork of a base class this was what I'm thinking about however the second option it gets difficult to have a multiple inheritance unless I'm missing something

We need to consider and decide the implementation details now because fundamentally the idea is clear there is a Grove and there is a inheritance and that is a clear but how do we implement it so one way I thinking is a for example if I want new class new repository and it is derived from two others for example and let's consider all the time the multiple inheritance for the for the sake of good example so multiple inheritance and we do two git sub modules in our repository so we create clean wrapper and we do clean with two git sub modules yeah this is interesting if all of them have a memory bank how do we resolve actually the diamond problem yeah because if two of them have the memory bank yeah this is actually interesting... However no as I'm thinking about it for example if two base like we are using two repositories for base classes for base repositories and both of them of course because groves fundamentally will probably have a memory bank so both of them will have their own memory bank since the memory bank of two different bases will have some different criteria for filtering it means two memory banks will be populated from two different perspectives that is not bad that is I think that can be made theoretically as a feature I'm not sure however I think it's still would be we need to consider whether it would not be more elegant to have the memory one memory bank so one memory bank even if two base repositories have their own memory bank yes and this is this is a diamond problem we need to consider it

Basically I think we need to take some doctrine of object oriented programming the issues that I'm trying to wrap my head around already solved — right? the guys who created c++ or something else

Case for having not just repositories semantically or philosophically inheriting each other but instead having Python classes having Python classes for example maybe not Python but some will be language classes and so that each repository delivers a class and it can it can have basically enforced the inheritance not by a new primitive but by python but by some maybe existing llm framework however I'm not sure about this

The reason why I would actually like to have the inheritance of repositories there are a few reasons number one this makes more accessible the creation and more primitive without interface to many people so it would be it becomes since there is llms and natural language programming and semantic context navigation I thought this is a good idea to start developing such approach second thing is to show the humanity the new paradigm not sure whether this is the biggest the best example but like to start thinking of it of like compiler that brings repositories together and inheritance of repositories and also because it is repository is essentially a directory so it's very primitive and it's everybody knows how to work with directories so it is like very simple very intuitive way to place files and to think about files. 
In other words the less code we have I'm thinking like this is my thinking so the more code we squeeze out of groves and put into the orchestrator and the more pure human readable text is in the Grove and the more forward compatible grows are they are if they are simple text files and memory of users without much infrastructure and however since there are just directors people can build their infrastructure there but there is a room to keep your grove pure as purely informational as possible or as purely natural text populated as possible and I'm just thinking intuitively it is very simple and very forward compatible because naturally the with time llms will become more and more efficient cheap productive systems will be much more advanced and thus the orchestrator level layer might get thinner in the future so the more actual ideas and thoughts are in groves and the more pure information is there the more time they can stand for they can they can age like fine wine people who have created the clean groves now just with their thoughts with their as a for example a perfect idea of a Grove is the meditations of Marcus Aurelius they are pure Grove and it can be broken down into filed into his book and people can just talk to Marcus Aurelius in a Grove maybe a rag could be applied to it but this shall not be done within a Grove his input can be just dumped in a grove and the orchestrator one day if we become very advanced maybe there will be some automatic RAG creation in memory there will be in-memory RAG if we want to one day but this is the problem of the orchestrator to see into the structure of the Grove and to maybe decide the best strategy how to deal with it this is what I'm thinking

I'll keep the implementation and the actual adoption very thin and focus on the approach and then the architecture to be very abstract and people if they want they can make a port for opencode if they want they can make a port for Claude whatever maybe some front end that they decide can be released the engine rather
