# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

FROM searxng/searxng:latest

COPY docker/clawdevs-searxng/limiter.toml /etc/searxng/limiter.toml

RUN set -eux; \
    cp /usr/local/searxng/searx/settings.yml /etc/searxng/settings.yml; \
    awk '\
      BEGIN { skip = 0 } \
      { \
        if ($0 ~ /^  - name: (google|ahmia|torch)$/) { skip = 1; next } \
        if (skip == 1) { \
          if ($0 ~ /^  - name: /) { skip = 0 } else { next } \
        } \
        print $0 \
      } \
    ' /etc/searxng/settings.yml > /etc/searxng/settings.yml.tmp; \
    mv /etc/searxng/settings.yml.tmp /etc/searxng/settings.yml; \
    sed -i 's/instance_name: "SearXNG"/instance_name: "ClawDevs Search"/g' /etc/searxng/settings.yml; \
    sed -i 's/default_lang: "auto"/default_lang: "pt-BR"/g' /etc/searxng/settings.yml; \
    awk '\
      { print } \
      /^  formats:$/ { \
        if (getline > 0) { \
          if ($0 ~ /^    - html$/) { \
            print $0; \
            print "    - json"; \
            next \
          } \
          print $0 \
        } \
      } \
    ' /etc/searxng/settings.yml > /etc/searxng/settings.yml.tmp; \
    mv /etc/searxng/settings.yml.tmp /etc/searxng/settings.yml
