\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{vitae}[2026/08/05 Executive portfolio system]
\LoadClass[10pt,a4paper]{article}
\RequirePackage{fontspec}
\RequirePackage{libertinus}
\RequirePackage{plex-sans}
\RequirePackage{geometry}
\RequirePackage{xcolor}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{tabularx}
\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{microtype}
\RequirePackage{ragged2e}
\RequirePackage{hyperref}
\RequirePackage{fancyhdr}
\RequirePackage{etoolbox}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\RequirePackage[backend=biber,style=authoryear,maxbibnames=12,doi=true,isbn=false,url=false]{biblatex}

\definecolor{OxfordBlue}{HTML}{12263A}
\definecolor{Slate}{HTML}{566674}
\definecolor{Mist}{HTML}{D8DEE2}
\definecolor{Warm}{HTML}{F4F2ED}
\definecolor{Accent}{HTML}{38647A}
\geometry{top=18mm,bottom=17mm,left=20mm,right=20mm,headheight=10mm,footskip=9mm}
\setmainfont{Libertinus Serif}
\setsansfont{IBM Plex Sans}
\setmonofont{IBM Plex Mono}
\AtBeginDocument{\RaggedRight\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}}
\emergencystretch=2em
\hypersetup{colorlinks=true,urlcolor=Accent,linkcolor=OxfordBlue,pdfauthor={Stephen Rudd},pdftitle={Stephen Rudd Executive Portfolio}}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\sffamily\scriptsize\color{Slate}\MakeUppercase{Stephen Rudd}}
\fancyhead[R]{\sffamily\scriptsize\color{Slate}\MakeUppercase{Building Computational Biology Capability}}
\fancyfoot[L]{\sffamily\tiny\color{Slate}Executive portfolio}
\fancyfoot[R]{\sffamily\tiny\color{Slate}\thepage}
\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}
\titleformat{\section}{\sffamily\Large\bfseries\color{OxfordBlue}}{}{0pt}{}[\vspace{2pt}\color{Mist}\titlerule]
\titleformat{\subsection}{\sffamily\normalsize\bfseries\color{OxfordBlue}}{}{0pt}{}
\titlespacing*{\section}{0pt}{12pt}{8pt}
\titlespacing*{\subsection}{0pt}{7pt}{3pt}
\setlist[itemize]{leftmargin=4mm,itemsep=1.5pt,topsep=3pt,parsep=0pt,label=\textcolor{Accent}{\raisebox{.25ex}{\tiny\textbullet}}}
\setlength{\bibitemsep}{5pt}
\renewcommand*{\bibfont}{\small\RaggedRight}

\newcommand{\VitaeHeader}[3]{%
  {\sffamily\fontsize{31}{32}\selectfont\color{OxfordBlue}\bfseries #1}\par\vspace{2pt}
  {\sffamily\large\color{Accent}#2}\par\vspace{7pt}
  {\sffamily\footnotesize\color{Slate}#3}\par\vspace{7pt}\color{Mist}\rule{\linewidth}{.7pt}\color{black}\vspace{2pt}}

\newenvironment{ExecutiveSummary}{\begin{quote}\color{OxfordBlue}\large\itshape\setlength{\leftskip}{4mm}\setlength{\rightskip}{4mm}}{\end{quote}}
\newenvironment{LeadershipAchievement}[1]{\par\medskip{\sffamily\bfseries\color{OxfordBlue}#1}\par\small}{\par}
\newenvironment{Employer}[4]{%
  \par\vspace{4pt}\noindent\begin{tabularx}{\linewidth}{@{}>{\RaggedRight\arraybackslash}X>{\RaggedLeft\arraybackslash}p{38mm}@{}}
  {\sffamily\bfseries\color{OxfordBlue}#1} & {\sffamily\scriptsize\color{Slate}#3}\\[-1pt]
  {\sffamily\small\color{Accent}#2} & {\sffamily\scriptsize\color{Slate}#4}
  \end{tabularx}\par\small}{\par\vspace{2pt}}
\newenvironment{CvEmployer}[4]{%
  \par\vspace{2pt}\noindent\begin{tabularx}{\linewidth}{@{}>{\RaggedRight\arraybackslash}X>{\RaggedLeft\arraybackslash}p{32mm}@{}}
  {\sffamily\small\bfseries\color{OxfordBlue}#1} -- {\sffamily\footnotesize\color{Accent}#2} & {\sffamily\scriptsize\color{Slate}#3, #4}
  \end{tabularx}\vspace{-2pt}\par\footnotesize}{\par}
\newenvironment{Programme}[1]{\begin{LeadershipAchievement}{#1}}{\end{LeadershipAchievement}}
\newenvironment{Publication}{\begin{quote}\small}{\end{quote}}
\newenvironment{Timeline}{\begin{center}\sffamily\footnotesize}{\end{center}}
\newenvironment{Quote}{\begin{quote}\color{OxfordBlue}\Large\itshape}{\end{quote}}
\newenvironment{CareerHighlight}[1]{\par\vspace{3pt}\noindent\begin{minipage}{\linewidth}\color{OxfordBlue}\rule{2pt}{\baselineskip}\hspace{5pt}{\sffamily\small\bfseries #1}\par\small\color{black}}{\end{minipage}\par\vspace{3pt}}
\newcommand{\RoleProgression}[1]{{\sffamily\scriptsize\bfseries\color{Accent}\MakeUppercase{#1}}}
\newcommand{\LeadershipArea}[2]{\noindent\begin{tabularx}{\linewidth}{@{}p{40mm}X@{}}\sffamily\small\bfseries\color{OxfordBlue}#1 & \small #2\end{tabularx}\par\vspace{3pt}}
\newcommand{\EducationEntry}[1]{\par{\small #1}\par}
\newcommand{\TalkEntry}[1]{\par{\small #1}\par}
\newcommand{\CareerTimeline}[6]{%
  \begin{Timeline}\begin{tikzpicture}[x=2.75cm]
  \draw[OxfordBlue,line width=.6pt] (0,0)--(5,0);
  \foreach \x/\label in {0/{#1},1/{#2},2/{#3},3/{#4},4/{#5},5/{#6}} {
    \fill[OxfordBlue] (\x,0) circle (1.5pt);
    \node[align=center,text width=2.45cm,font=\sffamily\scriptsize,text=OxfordBlue] at (\x,-.38) {\label};}
  \end{tikzpicture}\end{Timeline}}
\newcommand{\PortfolioPage}[2]{\clearpage\thispagestyle{fancy}{\sffamily\scriptsize\bfseries\color{Accent}\MakeUppercase{#1}}\par\vspace{4mm}{\sffamily\fontsize{25}{27}\selectfont\bfseries\color{OxfordBlue}#2}\par\vspace{7mm}}
\newcommand{\PageStatement}[1]{{\color{OxfordBlue}\Large\itshape #1}\par\vspace{6mm}}
