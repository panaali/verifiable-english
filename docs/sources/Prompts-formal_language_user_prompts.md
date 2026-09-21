# User Prompts — Formal / Verifiable English Discussion

All user prompts from this conversation, in chronological order.

## 1

Is it possible to write down any English statement in the L-E-A-N lean language?

## 2

Why auto formalization of math is hard? Isn't it easy to verify among all options and find what fits est?

## 3

Are there any better languages than English? Something synthetic that would allow to be talking formally and translating and has the capacity to be able to convey all meaning that English language has, basically translating from English to that formal language and then be able to convert back from that formal language back to English. Because English has so much ambiguity regarding what the person wants to say. I was wondering if, yeah, it should always be able to convert from that language, that formal language, to English. But as you said about Lean, it might be hard to, or, like, we can say that there could be multiple different interpretations of what the original English wanted to say in that formal language. Yeah, I just wonder if that language has syntax and could be basically spoken by human rather than Lean, which is hard and tough to read and talk for human.

## 4

When you had lojban, L-O-J-B-A-N, having more stars for broad everyday expressiveness than Ace, and less star for formal semantics, what was that trade-off? What was the issue there? Be concise.

## 5

Give me an example that helps me understand the difference between Lojban, ACE, and English.

## 6

For the Jack is a good doctor, both Lojban and Ace examples seem similar to me. Can you concisely teach me what's your point?

## 7

For this, every doctor treats a patient, what would be the Lojban writing of it?

## 8

Oh, it's not like English? It's based on which language?

## 9

And what's the ACE equivalent of that? Every doctor treats a patient.

## 10

Okay, so I like ACE. ACE seems to be very good that it looks like ordinary English and it can map to formal language. But then you mentioned that I had some ideas and there hasn't been a language like it. So I want to really understand in one specific example, what did you mean by ACE not supporting what the idea that you discussed?

## 11

What was the historical reason or, yeah, what was the root cause or root of they restricting ACE to be so narrow that even specifying such sentence is not possible without introducing so many, or, like, writing it so explicitly? Be concise.

## 12

What do you mean by software specifications in that context? Be super concise.

## 13

And how about Logban? What was the historical reason of building it that way? And you mentioned that it's not possible to convert Logban directly to formal logic or Lean. Is that right?

## 14

Do you think that it's possible to expand ACE, like having Ace++, type of language, which still provide the formalization and everyday English part of the ACE? Yeah, so I'm going towards the idea that I initially introduced. And how difficult it would be to prove that we are keeping all the properties that ACE has by introducing these new things to ACE. Do a little deep research, understand ACE. I think ACE is open source. Is that right? If so, read the code, read documentation, and tell me how difficult it would be to expand it, but also cleanly prove that we are still adhering to the properties that ACE has.

## 15

Your message was very long, I didn't have time to read it. Summarize your main points. Be concise.

## 16

Why they didn't make a fully machine verified? It's weird that they're relying on tests.

## 17

Coq/Isabelle/Lean-like
What did you mean by mentioning these names? What's specific about them?

## 18

Do you know about TLA Plus? What do you think about that compared to what we have mentioned? Read a bit about it and be very concise.

## 19

How does this Example look like in ace

## 20

So it's not even possible to specify it him as?

## 21

Do a bit of deep dive and see if X++ is already built. Maybe there are other languages that you haven't considered or you're not aware of. So you might need to do a bit of more deep research about this.

## 22

Okay. I see lots of good ideas. If we are gonna build this idea that I have, where should we start? Do you think we should start with the ACE project itself and do what you mentioned regarding machine-proved semantics? Or do you think we should start from Pang, PangLite, with event calculus, Freteish, or the canonical English? Yeah. Which one of those could be where we can start? We can even help any of these projects if they're aligned with what we want. Basically we just help them and get what we want.

## 23

Learn a bit about GPT-6 Astra, which is you, and Fable 5.1 from Anthropic, regarding their ability to write Lean code and, in general, software engineering. I just want to know how capable are they, and then tell me which of the above suggestions that you had, the preferred path that you mentioned, might be. You might want to change it, or you think that it's a good plan. I just want to highlight that using GPT-6 or Fable 5.1, it's very easy to write any software, and I believe it's very easy to also write Lean code. The only issue is I'm not very expert in Lean or formal logic, but I believe GPT-6 or Fable 5.1 might be able to help. I just want you to revise the path that you mentioned and think how can we do it the best using what's available.

## 24

Why not building on top of Canonical English project? Why not fork that one instead? Pros and cons versus the plan that you brought?

## 25

Search a bit more, maybe you can find the CE's GitHub.

## 26

What's interesting about Common Canonical English is it is so much tied to machine-to-machine or like agent-to-agent communication. If I understand correctly, that's what they mentioned, which is similar to my intention of using this language for human-to-agent communication and, or, yeah, agent-to-agent communication. By the way, what is this Noah parser, or like Noah, N-O-A-H? Is this like another project that Canonical English has used? Can we also use those?

## 27

So the formal guarantee is not about the Rust implementation, right? So for example, if I'm going to implement my new project in Rust, the lean would not help with that. What would it help?

## 28

Okay, good ideas about the additional step. Which one of these are more possible and give us the 100% accuracy that we are aiming for?

## 29

I wonder why no one has built such a thing yet. It seems something very helpful if we have it, don't you think so? I guess it can also be used for proving the math papers and, you know, for example, whatever people do in Lean, we should be able to do it in this new language. Is that true? For example, recently Anthropic and OpenAI released or solved a few open problems, and to prove that they were right, they used Lean. I wonder if we should be able to use this new language for proving all of them similarly, rather than using Lean.

## 30

This is good. Do you think I would be able to convert any paper in physics and write it in this language? I'm referring to seminal paper in physics, such that we can verify if the paper is coherent and if it misses anything or not. You know what I'm saying? So basically we write the paper. So there are two methods that we can use. One is that we ask the authors to write the papers, their papers in this C++. which would then give them the guarantee that, you know, it's coherent and everything is explicit and there are no different interpretations or, like, no ambiguity about what they want to say. And the other way to do it is to just take one paper off the shelf, write it using this language, and then show if it has any issues or not, or if it has any implicit assumptions that were not clearly elaborated in the paper. What do you think about this?

## 31

Sorry, I forgot which one of these three now you recommend? prove the Rust implementation equivalent to the Lean specification, use a Rust verification system, or generate part of the executable from verified code.

## 32

If the speed of execution of our language is very critical and important, which one of these do you think is best?

## 33

Compare Rust versus C language for this project. Be very concise, especially regarding this verification parts.

## 34

Remember that we are going to write the code using Fable 5.1 or Astra. Do a bit of search and think more and decide what's the best option for us.

## 35

How hard it would be to have the verified compiler to machine code for Rust? Assume that Astra and Fable will do all the work for us.

## 36

Given what we discussed regarding this new language, think about U.S. Constitution and Anthropic Cloud Constitution. Is it possible to convert this to C++? For the U.S. Constitution, we can also use the Supreme Court rulings to help us interpret part of it that is not very well defined, or part of it that are not formally defined.

## 37

You say version. What do you mean here? You mentioned version a few times. Be very concise.

## 38

What does canonical English mean? I mean, what does canonical mean here? And do you think C++ is a good name? Do you have any better suggestions?

## 39

Thanks, could you write an md with all the prompts I sent you?
