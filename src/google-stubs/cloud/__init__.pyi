# google.cloud is a namespace package at runtime. This empty stub stops pyright from reporting
# `from google.cloud import storage` as missing stubs; modules not stubbed here still resolve to the
# installed libraries, as py.typed marks the stubs partial.
