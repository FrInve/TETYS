# TETYS

## Topics' Evolution That You See

<img width="697" alt="image" src="https://github.com/user-attachments/assets/1d20199b-8bbb-4e15-98a2-720c22f1d381">

### Project information

Topics Evolution That You See (TETYS) is a beneficiary of the NGI Search 2nd Call. 
**NGI Search** is within the EU programme HORIZON-CL4-2021-HUMAN-01; it has received funding from the **European Union’s Horizon Europe** research and innovation programme under the **grant agreement n. 101069364** and it is framed under Next Generation Internet Initiative.

**Duration of the program: September 2023-September 2024**

### Onboarding

TETYS proposes the next-generation open-source **_Web topic explorer_** inspecting a big textual corpus, projecting results on a dashboard of topic trends with easy-to-drive statistical testing. It is composed of
1. a pipeline for ingesting huge data corpora, extracting highly relevant topics, clustered along orthogonal dimensions
1. an interactive dashboard, supporting topic visualization as word clouds and exploration of temporal series.

The first [CorToViz prototype](http://geco.deib.polimi.it/cortoviz/) explores the CORD-19 dataset (COVID-19 / SARS-CoV-2 virus research abstracts). Many different domains can be explored using TETYS (e.g., climate change and controversial debates on social media).

-----------------------------------------------------------------
Our full documentation is on [our WIKI page](https://github.com/FrInve/TETYS/wiki).
-----------------------------------------------------------------

### What was our starting point?

CORToViz is the first research demonstrator showcasing the TETYS approach

### How far did we get during one year of the project?

We consolidated the first demonstrator 1) making the pipeline applicable to any corpus of Web textual documents, and 2) validating the dashboard experience with user studies
We tested our solution on other domains (e.g., climate change) and built a new -more mature- product, that allows to explore topics on the United Nations's [Sustainable Development Goals (SDGs)](https://sdgs.un.org/goals) in the scientific literature.

### How does the SDG-TETYS look like now?
<img width="1498" alt="image" src="https://github.com/user-attachments/assets/53898f1c-139b-416d-a16c-ccb593ac8a56">

The TETYS dashboard allows to directly inspect the results obtained by our pipeline, supporting users in the exploration of topics, which would be a tedious and time-consuming task if performed manually. Users are asked to select one macro-area out of the five offered. 

These two possibilities allow the user to access two possible pages:
the *Single Topic* page (Panel A) or the *Topic Comparison* page (see Panels B/C).
Panel A shows a descriptive card of the topic with its description as wordcloud and star diagram, a panel for performing two-interval or multi-interval comparisons between user-selected time spans of the topic time series, and a downloadable list of publications that are assigned to the topic.
Panel B shows a set of topics that have been selected by the user from the pool of topics related to the searched keyword; the user can select topics also during multiple consecutive searches (as it happened in Panel C). 
Topics time series are shown on the same graph, where users can (de)select tracks as needed and use a slider to select the interesting time span.
Different time resolutions can be set; the relative frequencies of the topics in one specific time instant can be visualized on hover.

<img width="1612" alt="image" src="https://github.com/user-attachments/assets/8a2ec482-abf7-412b-8766-244c99749b7a">

### What is our information architecture?

<img width="1110" alt="image" src="https://github.com/user-attachments/assets/ed78951c-4ec9-4f47-8685-94ef4a69f9ed">

The frontend contains a Web application working as a \textbf{Client} with functionalities that allow users to select a macro-area of interest, filter the content of the topic model using keywords or specific publications' DOI, visualize the content and download it (plots and tables).
The backend contains four modules. 
Data persistence is taken care of in the \textbf{Database} (collecting publications metadata and information describing the topics) and in the \textbf{Topic Model registry}, which stores the topics models of the project as large \textit{pickle} objects.

These two models can be queried by the central \textbf{Server}, i.e., the orchestrator of TETYS: this includes a project registry along with services to perform keyword-based search and similarity-based search over the five different projects (one per macro-area), which continue to send and receive data. 
In each project, we allow analysis (i.e., statistical testing) and results download.
Keyword-based search is exploited to find ranked topics that are close (i.e., relevant to) specific keywords. Similarity-based search is exploited to find ranked topics that are relevant to a specific point in the embedding space, i.e., one abstract -- identified through its DOI. These search procedures make use of *External services* such as Scopus APIs. 
Note that the Model registry contains the models that, for each project, infer the most relevant topics for any query, both keywords-based and DOI-based.

-----------------------------------------------------------------

## Projects activities track

**October 5th, 2023**:
Our preprint on CORToViz is on ArXiv! Check it out [on arXiv](https://arxiv.org/abs/2310.03928).

**November 1st, 2023**: 
A first prototype on Climate Change Scientific articles is available at [http://gmql.eu/climviz](http://geco.deib.polimi.it/climviz/)!

**November 10th, 2023**: 
The project has been presented at the [SFSCON conference](https://www.sfscon.it/programs/2023/) by Francesco Invernici, NOI TechPark – Bolzano/Italy. Nov. 10th-11th, 2023. See the [video and slides](https://www.sfscon.it/talks/the-cord-19-topic-visualizer/).

**February 2nd, 2024**: 
Anna has been interviewed by NGI Search on our TETYS Project. See the full interview on [The Next Generation Internat (NGI) Community on Funding Box](https://spaces.fundingbox.com/spaces/ngi-community-ngi-innovators/65bcb5c082e68c5758327104).

**March 4th, 2024**: 
Our Master Student Jelena has joined the team to help us improve the data extraction phase and compare BERTopic stages with more up-to-date technologies.

**April 8th, 2024**: 
TETYS has been presented in the Department of Electronics, Information and Bioengineering at Politecnico di Milano (see [here](https://www.deib.polimi.it/eng/european-projects/details/499)).

**May 2nd, 2024**:
Our Master Students Francesca and Amir have joined the team to help us improve the User experience and statistical tests.

**June 7th, 2024**: Anna presented the TETYS project in the context of the Research Project Exhibition at the CAiSE Conference (Limassol, Cyprus)
(see Poster [here](https://github.com/user-attachments/files/16032054/Bernasconi_CAiSE_2024_RPE_TETYS.pdf))

**August 31st, 2024**: our mature solution for exploring Sustainable Development Goals in scientific literature has been realeased at [https://gmql.eu/tetys](https://geco.deib.polimi.it/tetys)

We are still working on testing and validating the application. 
More to come on applying TETYS to other domains ( ...like legislative text :) 



-----------------------------------------------------------------
Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or European Commission. Neither the European Union nor the granting authority can be held responsible for them. Funded within the framework of the NGI Search project under grant agreement No 101069364

https://www.ngi.eu/ngi-projects/ngi-search/
![image](https://github.com/user-attachments/assets/add67eed-e98f-4e42-a903-55ce125e37fe)
![image](https://github.com/user-attachments/assets/0bc43f7f-81ed-4a2a-84a9-8ae145c8bf1e)


