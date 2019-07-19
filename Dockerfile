FROM amazonlinux:latest

RUN yum install tar bzip2 git -y

RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --output miniconda-installer.sh && \
    chmod +x miniconda-installer.sh

RUN ./miniconda-installer.sh -b -p /opt/conda && \
    rm miniconda-installer.sh

# RUN git checkout http://gitlab.com/ddga_site/latest
RUN /opt/conda/bin/conda create -p /opt/env -y python jinja2 flask boto3 -y && \
    rm -rf /opt/conda

RUN mkdir /opt/ddga_site
RUN mkdir /opt/ddga_site/views
COPY ddga_site.py /opt/ddga_site/
COPY views/scores_table.html views/scores_table.html
RUN chmod +x /opt/ddga_site/ddga_site.py

ENV APP_SCRIPT=/opt/ddga_site/ddga_site.py

EXPOSE 80
CMD "/opt/env/bin/python" "/opt/ddga_site/ddga_site.py"
