The first run without reranking was already working quite well.
It returned the same extracts from the main text as the reranked one.
Both find the relevant information in page 40 to answer the query in the example below.

============================================================
Evaluate Performance (With & Without Reranking)
============================================================

Query: What are the components of Trustworthy AI?

--- Retrieval WITHOUT Reranking ---
Results: 6
Top score: 0.8375

--- Retrieval WITH Reranking ---
Results: 6
Top score: 0.8699
Score improvement: 3.90%

--- Detailed Results Comparison ---
{
  "without_reranking": [
    {
      "metadata": {
        "body": "The principles outlined in Chapter I must be translated into concrete requirements to achieve Trustworthy AI. These requirements are applicable to different stakeholders partaking in AI systems\u2019 life cycle: developers, deployers and end-users, as well as the broader society. By developers, we refer to those who research, design and/or develop AI systems. By deployers, we refer to public or private organisations that use AI systems within their business processes and to offer products and services to others. End-users are those engaging with the AI system, directly or indirectly. Finally, the broader society encompasses all others that are directly or indirectly affected by AI systems. Different groups of stakeholders have different roles to play in ensuring that the requirements are met: a. Developers should implement and apply the requirements to design and development processes; b. Deployers should ensure that the systems they use and the products and services they offer meet the requirements; c. End-users and the broader society should be informed about these requirements and able to request that they are upheld. The below list of requirements is non-exhaustive. It includes systemic, individual and societal aspects: ",
        "level": "section",
        "page": 16.0
      },
      "page_content": "1. Requirements of Trustworthy AI",
      "combined_score": 0.837455571
    },
    {
      "metadata": {
        "body": "Trustworthy AI has three components: (1) it should be lawful, ensuring compliance with all applicable laws and regulations (2) it should be ethical, demonstrating respect for, and ensure adherence to, ethical principles and values and (3) it should be robust, both from a technical and social perspective, since, even with good intentions, AI systems can cause unintentional harm. Trustworthy AI concerns not only the trustworthiness of the AI system itself but also comprises the trustworthiness of all processes and actors that are part of the system\u2019s life cycle. ",
        "level": "section",
        "page": 40.0
      },
      "page_content": "Trustworthy AI",
      "combined_score": 0.814342
    },
    {
      "metadata": {
        "body": "This Chapter sets out the foundations of Trustworthy AI, grounded in fundamental rights and reflected by four ethical principles that should be adhered to in order to ensure ethical and robust AI. It draws heavily on the field of ethics. AI ethics is a sub-field of applied ethics, focusing on the ethical issues raised by the development, deployment and use of AI. Its central concern is to identify how AI can advance or raise concerns to the good life of individuals, whether in terms of quality of life, or human autonomy and freedom necessary for a democratic society. Ethical reflection on AI technology can serve multiple purposes. First, it can stimulate reflection on the need to protect individuals and groups at the most basic level. Second, it can stimulate new kinds of innovations that seek to foster ethical values, such as those helping to achieve the UN Sustainable Development Goals , which are firmly embedded in the forthcoming EU Agenda 2030. While this document mostly concerns itself with the first purpose mentioned, the importance that ethics could have in the second should not be underestimated. Trustworthy AI can improve individual flourishing and collective wellbeing by generating prosperity, value creation and wealth maximization. It can contribute to achieving a fair society, by helping to increase citizens\u2019 health and well-being in ways that foster equality in the distribution of economic, social and political opportunity. It is therefore imperative that we understand how to best support AI development, deployment and use to ensure that everyone can thrive in an AI-based world, and to build a better future while at the same time being globally competitive. As with any powerful technology, the use of AI systems in our society raises several ethical challenges, for instance relating to their impact on people and society, decision-making capabilities and safety. If we are increasingly going to use the assistance of or delegate decisions to AI systems, we need to make sure these systems are fair in their impact on people\u2019s lives, that they are in line with values that should not be compromised and able to act accordingly, and that suitable accountability processes can ensure this. Europe needs to define what normative vision of an AI-immersed future it wants to realise, and understand which notion of AI should be studied, developed, deployed and used in Europe to achieve this vision. With this document, we intend to contribute to this effort by introducing the notion of Trustworthy AI, which we believe is the right way to build a future with AI. A future where democracy, the rule of law and fundamental rights underpin AI systems and where such systems continuously improve and defend democratic culture will also enable an environment where innovation and responsible competitiveness can thrive. A domain-specific ethics code \u2013 however consistent, developed and fine-grained future versions of it may be \u2013 can never function as a substitute for ethical reasoning itself, which must always remain sensitive to contextual details that cannot be captured in general Guidelines. Beyond developing a set of rules, ensuring Trustworthy AI requires us to build and maintain an ethical culture and mind-set through public debate, education and practical learning. ",
        "level": "chapter",
        "page": 11.0
      },
      "page_content": "I. Chapter I: Foundations of Trustworthy AI",
      "combined_score": 0.77206862
    }
  ],
  "with_reranking": [
    {
      "metadata": {
        "body": "Trustworthy AI has three components: (1) it should be lawful, ensuring compliance with all applicable laws and regulations (2) it should be ethical, demonstrating respect for, and ensure adherence to, ethical principles and values and (3) it should be robust, both from a technical and social perspective, since, even with good intentions, AI systems can cause unintentional harm. Trustworthy AI concerns not only the trustworthiness of the AI system itself but also comprises the trustworthiness of all processes and actors that are part of the system\u2019s life cycle. ",
        "level": "section",
        "page": 40.0
      },
      "page_content": "Trustworthy AI",
      "combined_score": 0.8698728717815465
    },
    {
      "metadata": {
        "body": "The principles outlined in Chapter I must be translated into concrete requirements to achieve Trustworthy AI. These requirements are applicable to different stakeholders partaking in AI systems\u2019 life cycle: developers, deployers and end-users, as well as the broader society. By developers, we refer to those who research, design and/or develop AI systems. By deployers, we refer to public or private organisations that use AI systems within their business processes and to offer products and services to others. End-users are those engaging with the AI system, directly or indirectly. Finally, the broader society encompasses all others that are directly or indirectly affected by AI systems. Different groups of stakeholders have different roles to play in ensuring that the requirements are met: a. Developers should implement and apply the requirements to design and development processes; b. Deployers should ensure that the systems they use and the products and services they offer meet the requirements; c. End-users and the broader society should be informed about these requirements and able to request that they are upheld. The below list of requirements is non-exhaustive. It includes systemic, individual and societal aspects: ",
        "level": "section",
        "page": 16.0
      },
      "page_content": "1. Requirements of Trustworthy AI",
      "combined_score": 0.75
    },
    {
      "metadata": {
        "body": "This Chapter sets out the foundations of Trustworthy AI, grounded in fundamental rights and reflected by four ethical principles that should be adhered to in order to ensure ethical and robust AI. It draws heavily on the field of ethics. AI ethics is a sub-field of applied ethics, focusing on the ethical issues raised by the development, deployment and use of AI. Its central concern is to identify how AI can advance or raise concerns to the good life of individuals, whether in terms of quality of life, or human autonomy and freedom necessary for a democratic society. Ethical reflection on AI technology can serve multiple purposes. First, it can stimulate reflection on the need to protect individuals and groups at the most basic level. Second, it can stimulate new kinds of innovations that seek to foster ethical values, such as those helping to achieve the UN Sustainable Development Goals , which are firmly embedded in the forthcoming EU Agenda 2030. While this document mostly concerns itself with the first purpose mentioned, the importance that ethics could have in the second should not be underestimated. Trustworthy AI can improve individual flourishing and collective wellbeing by generating prosperity, value creation and wealth maximization. It can contribute to achieving a fair society, by helping to increase citizens\u2019 health and well-being in ways that foster equality in the distribution of economic, social and political opportunity. It is therefore imperative that we understand how to best support AI development, deployment and use to ensure that everyone can thrive in an AI-based world, and to build a better future while at the same time being globally competitive. As with any powerful technology, the use of AI systems in our society raises several ethical challenges, for instance relating to their impact on people and society, decision-making capabilities and safety. If we are increasingly going to use the assistance of or delegate decisions to AI systems, we need to make sure these systems are fair in their impact on people\u2019s lives, that they are in line with values that should not be compromised and able to act accordingly, and that suitable accountability processes can ensure this. Europe needs to define what normative vision of an AI-immersed future it wants to realise, and understand which notion of AI should be studied, developed, deployed and used in Europe to achieve this vision. With this document, we intend to contribute to this effort by introducing the notion of Trustworthy AI, which we believe is the right way to build a future with AI. A future where democracy, the rule of law and fundamental rights underpin AI systems and where such systems continuously improve and defend democratic culture will also enable an environment where innovation and responsible competitiveness can thrive. A domain-specific ethics code \u2013 however consistent, developed and fine-grained future versions of it may be \u2013 can never function as a substitute for ethical reasoning itself, which must always remain sensitive to contextual details that cannot be captured in general Guidelines. Beyond developing a set of rules, ensuring Trustworthy AI requires us to build and maintain an ethical culture and mind-set through public debate, education and practical learning. ",
        "level": "chapter",
        "page": 11.0
      },
      "page_content": "I. Chapter I: Foundations of Trustworthy AI",
      "combined_score": 0.48162870425813153
    }
  ]
}