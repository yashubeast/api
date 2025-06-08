FROM python:3.11-slim

# set working directory
WORKDIR /opt/app

# install git and other dependencies
RUN apt-get update && \
	apt-get install -y git && \
	apt-get clean

# clone the repository
RUN git clone https://github.com/yashubeast/api.git .

# create non-root user and group
RUN addgroup --system app && \
	adduser --system --ingroup app --home /opt/app app
	
# change ownership
RUN chown -R app:app /opt/app && \
	chmod +x run.sh

# switch to non-root user
USER app

# create python virtual environment
RUN python -m venv .venv && \
	.venv/bin/pip install --no-cache-dir -r req.txt

# set virtual environment
ENV PATH="/opt/app/.venv/bin:$PATH"

# run the bot
CMD ["./run.sh"]