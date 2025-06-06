# ==============================build stage==============================
FROM python:3.11-slim AS builder

WORKDIR /build

# install git and other dependencies
RUN apt-get update && \
	apt-get install -y git && \
	apt-get clean

# clone the repository
RUN git clone https://github.com/yashubeast/api.git .

# create python virtual environment
RUN python -m venv .venv && \
	.venv/bin/pip install --no-cache-dir -r req.txt

# ==============================final stage==============================
FROM python:3.11-slim

# install git and other dependencies
RUN apt-get update && \
	apt-get install -y git && \
	apt-get clean

# create non-root user and group
RUN addgroup --system api && \
	adduser --system --ingroup api --home /opt/api api

# set working directory
WORKDIR /opt/api

# copy the installed packages from the builder stage
COPY --from=builder /build /opt/api

# change ownership
RUN chown -R api:api /opt/api && \
	chmod +x run.sh

# switch to non-root user
USER api

# set virtual environment
ENV PATH="/opt/api/.venv/bin:$PATH"

# run the bot
CMD ["./run.sh"]