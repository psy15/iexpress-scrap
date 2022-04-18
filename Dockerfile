FROM python:3.10-slim

ENV GTOKEN=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 \
    TOKEN=2129546944:AAFF2_n8dKud30QPhx3-vqlhtpZeiKEzwzs \
    TARGET_URL=https://indianexpress.com/section/explained/ \
    CHANNEL=@ie_test \
    GIST_ID=3c9e2ec8af21af70307edeadfc7120cb


RUN mkdir -p /home/app

COPY ./app /home/app
WORKDIR /home/app

RUN pip install pipenv && \
  apt-get update && \
  apt-get install -y --no-install-recommends gcc python3-dev libssl-dev && \
  pipenv install --deploy

CMD ["pipenv","run", "python", "app.py"]