FROM python:3.12-slim

ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

WORKDIR /app
# Run updates
RUN apt-get clean && apt-get update && apt-get install -y locales gcc && locale-gen en_US.UTF-8 && apt-get upgrade -y

#Install required python packages
COPY . ./
RUN pip install poetry && poetry install --without dev

CMD ["imgrott"]