ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

__TECHNO_PROJECT_VERSION_FILE:=VERSION
__TECHNO_PROJECT_BUILD_NUM_FILE:=.build_num
TEMPLATE_DIR=$(ROOT_DIR)/template
VERSION := $(file < $(__TECHNO_PROJECT_VERSION_FILE))
BUILD_NUM := $(file < $(__TECHNO_PROJECT_BUILD_NUM_FILE))

echo:

	@echo "v$(VERSION) (build $(BUILD_NUM))"
	@echo "ROOT_DIR: $(ROOT_DIR)"

build: _ibn

	@python3 $(TEMPLATE_DIR)/gen.py --config="{\"VERSION\":\"\\\"$(VERSION)\\\"\"}" --template="$(TEMPLATE_DIR)/pyproject.template.toml" --out="pyproject.toml"
	@python3 -m build

gittag:

	@git tag v$(VERSION)
	@git push origin v$(VERSION)

# --- Version Number Targets ---

_imaj:

	@echo "Incrementing Major Version"
	@awk -F. '{$$1+=1; $$2=0; $$3=0} 1' OFS=. $(__TECHNO_PROJECT_VERSION_FILE) > temp && mv temp $(__TECHNO_PROJECT_VERSION_FILE)
	$(eval VERSION := $(shell cat $(__TECHNO_PROJECT_VERSION_FILE)))
	$(eval BUILD_NUM := $(shell cat $(__TECHNO_PROJECT_BUILD_NUM_FILE)))

	@VERSION=$$(cat $(__TECHNO_PROJECT_VERSION_FILE)) && BUILD_NUM=$$(cat $(__TECHNO_PROJECT_BUILD_NUM_FILE)) && \
		echo "$(shell date) incr. major\t | $$VERSION build $$BUILD_NUM | $(TAG)" >> .version_log && \
		echo "$(VERSION) (build $(BUILD_NUM)) -> $$VERSION (build $$BUILD_NUM)"

_imin:

	@echo "Incrementing Minor Version"
	@awk -F. '{$$2+=1; $$3=0} 1' OFS=. $(__TECHNO_PROJECT_VERSION_FILE) > temp && mv temp $(__TECHNO_PROJECT_VERSION_FILE)
	@VERSION=$$(cat $(__TECHNO_PROJECT_VERSION_FILE)) && BUILD_NUM=$$(cat $(__TECHNO_PROJECT_BUILD_NUM_FILE)) && \
		echo "$(shell date) incr. minor\t | $$VERSION build $$BUILD_NUM | $(TAG)" >> .version_log && \
		echo "$(VERSION) (build $(BUILD_NUM)) -> $$VERSION (build $$BUILD_NUM)"

_ipat:

	@echo "Incrementing Patch Version"
	@awk -F. '{$$3+=1} 1' OFS=. $(__TECHNO_PROJECT_VERSION_FILE) > temp && mv temp $(__TECHNO_PROJECT_VERSION_FILE)
	@VERSION=$$(cat $(__TECHNO_PROJECT_VERSION_FILE)) && BUILD_NUM=$$(cat $(__TECHNO_PROJECT_BUILD_NUM_FILE)) && \
		echo "$(shell date) incr. patch\t | $$VERSION build $$BUILD_NUM | $(TAG)" >> .version_log && \
		echo "$(VERSION) (build $(BUILD_NUM)) -> $$VERSION (build $$BUILD_NUM)"

_ibn:

	@echo "Incrementing Build Version:"
	@awk -F. '{$$1+=1} 1' OFS=. $(__TECHNO_PROJECT_BUILD_NUM_FILE) > temp && mv temp $(__TECHNO_PROJECT_BUILD_NUM_FILE)
	@VERSION=$$(cat $(__TECHNO_PROJECT_VERSION_FILE)) && BUILD_NUM=$$(cat $(__TECHNO_PROJECT_BUILD_NUM_FILE)) && \
		echo "$(shell date) incr. build\t | $$VERSION build $$BUILD_NUM | $(TAG)" >> .version_log && \
		echo "$(VERSION) (build $(BUILD_NUM)) -> $$VERSION (build $$BUILD_NUM)"

_zpat:

	@echo "Zeroing Patch Version"
	@awk -F. '{$$3=0} 1' OFS=. $(__TECHNO_PROJECT_VERSION_FILE) > temp && mv temp $(__TECHNO_PROJECT_VERSION_FILE)
	@VERSION=$$(cat $(__TECHNO_PROJECT_VERSION_FILE)) && BUILD_NUM=$$(cat $(__TECHNO_PROJECT_BUILD_NUM_FILE)) && \
		echo "$(shell date) zero patch\t | $$VERSION build $$BUILD_NUM | $(TAG)" >> .version_log && \
		echo "$(VERSION) (build $(BUILD_NUM)) -> $$VERSION (build $$BUILD_NUM)"