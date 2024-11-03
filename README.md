# TETYS: Topics' Evolution That You See

### Project information

<img width="297" alt="image" src="https://github.com/user-attachments/assets/1d20199b-8bbb-4e15-98a2-720c22f1d381">

Topics Evolution That You See (TETYS) is a beneficiary of the NGI Search 2nd Call. 
**NGI Search** is within the EU programme HORIZON-CL4-2021-HUMAN-01; it has received funding from the **European Union’s Horizon Europe** research and innovation programme under the **grant agreement n. 101069364** and it is framed under Next Generation Internet Initiative.

**Duration of the program: September 2023-September 2024**

<img src="https://www.ngisearch.eu/download/FlamingoThemes/NGISearch2/NGISearch_logo_tag_icon.svg?rev=1.1" width="300">
<br>
<br>
<img src="https://github.com/user-attachments/assets/a3283b38-f8d9-4ff8-965c-541229484232" width="150">

---

See [our WIKI page](https://github.com/FrInve/TETYS/wiki) for full documentation.

---

### What is TETYS?

TETYS proposes the next-generation open-source **_Web topic explorer_** inspecting a big textual corpus, projecting results on a dashboard of topic trends with easy-to-drive statistical testing. It is composed of
1. a pipeline for ingesting huge data corpora, extracting highly relevant topics, clustered along orthogonal dimensions
1. an interactive dashboard, supporting topic visualization as word clouds and exploration of temporal series.

### What was our starting point?

[CORToViz](http://geco.deib.polimi.it/cortoviz/) is the first demonstrator showcasing the TETYS approach. It explores the CORD-19 dataset (COVID-19 / SARS-CoV-2 virus research abstracts). Many different domains can be explored using TETYS.

### How far did we get during the one-year project?

We consolidated the first demonstrator 1) making the pipeline applicable to any corpus of Web textual documents, and 2) validating the dashboard experience with user studies
We tested our solution on other domains (e.g., climate change) and built a new -more mature- product, that allows us to explore topics on the United Nations's [Sustainable Development Goals (SDGs)](https://sdgs.un.org/goals) in the scientific literature.

### How does the SDG-TETYS look like now?

The TETYS dashboard allows us to directly inspect the results obtained by our pipeline, supporting users in the exploration of topics. Users are asked to select one macro-area out of the five offered. 

<img width="800" alt="image" src="https://github.com/user-attachments/assets/53898f1c-139b-416d-a16c-ccb593ac8a56">

Users can explore two kinds of pages: 
1. the *Single Topic* page (Panel A): it shows a descriptive card of the topic with a wordcloud description and star diagram, a panel for performing two-interval or multi-interval comparisons between user-selected time spans of the topic time series, and a downloadable list of publications that are assigned to the topic.
2. the *Topic Comparison* page (see Panels B/C): it shows a set of topics that have been selected by the user from the pool of topics related to the searched keyword; the user can select topics also during multiple consecutive searches (see Panel C).

<img width="800" alt="image" src="https://github.com/user-attachments/assets/8a2ec482-abf7-412b-8766-244c99749b7a">

### What is our information architecture?

The frontend contains a Web application working as a *Client* with functionalities that allow users to select a macro-area of interest, filter the content of the topic model using keywords or specific publications' DOI, visualize the content, and download it (plots and tables). The backend contains four modules. 
Data persistence is taken care of in the *Database* (collecting publications metadata and information describing the topics) and in the *Topic Model registry*, which stores the topics models of the project as large `pickle` objects. These two models can be queried by the central *Server*, i.e., the orchestrator of TETYS: this includes a project registry along with services to perform keyword-based search and similarity-based search over the five different projects (one per macro-area). 
Keyword-based search is exploited to find ranked topics that are close (i.e., relevant to) specific keywords. Similarity-based search is exploited to find ranked topics that are relevant to a specific point in the embedding space, i.e., one abstract -- identified through its DOI.

<img width="800" alt="image" src="https://github.com/user-attachments/assets/ed78951c-4ec9-4f47-8685-94ef4a69f9ed">


---

### Projects activities track

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

**June 25th, 2024**: We had a fruitful discussion with Linknovate and explored our possible market's landscape with their tool.

**August 31st, 2024**: our mature solution for exploring Sustainable Development Goals in scientific literature has been released at [https://gmql.eu/tetys](https://geco.deib.polimi.it/tetys)

**September 27th, 2024**: Anna was interviewed by a researcher at the Department of Business Development and Technology, Aarhus University exploring several aspects of our NGI Search project.

We are still working on testing and validating the application. 
More to come on applying TETYS to other domains ( ...like legislative text :) 

---

## Citation

Please, consider citing this work in your research as:

Bernasconi, A., Invernici, F., & Ceri, S. (2024). TETYS: Towards the Next-Generation Open-Source Web Topic Explorer. In CEUR WORKSHOP PROCEEDINGS (Vol. 3692, pp. 26-33). CEUR-WS. [https://ceur-ws.org/Vol-3692/paper4.pdf](https://ceur-ws.org/Vol-3692/paper4.pdf)

```bibtex
@inproceedings{bernasconi2024tetys,
  title={TETYS: Towards the Next-Generation Open-Source Web Topic Explorer},
  author={Bernasconi, Anna and Invernici, Francesco and Ceri, Stefano and others},
  booktitle={CEUR WORKSHOP PROCEEDINGS},
  volume={3692},
  pages={26--33},
  year={2024},
  organization={CEUR-WS}
}
```

Invernici, F., Bernasconi, A., & Ceri, S. (2024). Exploring the evolution of research topics during the COVID-19 pandemic. Expert Systems with Applications, 252, 124028. [https://doi.org/10.1016/j.eswa.2024.124028](https://doi.org/10.1016/j.eswa.2024.124028)

```bibtex
@article{invernici2024exploring,
  title={Exploring the evolution of research topics during the COVID-19 pandemic},
  author={Invernici, Francesco and Bernasconi, Anna and Ceri, Stefano},
  journal={Expert Systems with Applications},
  volume={252},
  pages={124028},
  year={2024},
  publisher={Elsevier}
}
```


