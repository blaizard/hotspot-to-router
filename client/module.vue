<template>
	<div class="module">
        <div class="module-status" @click="handleClick">
            <slot name="status">
                <span v-if="icon" :class="icon"></span>
                {{ title }}
            </slot>
        </div>
        <div v-show="active" ref="body" class="module-body">
            <slot name="body" :close="handleClose"></slot>
        </div>
	</div>
</template>

<script>
	"use strict"

	export default {
        props: {
            title: {type: String, required: false, default: ""},
            icon: {type: String, required: false, default: ""},
            onclick: {type: Function, required: false, default: () => {}},
        },
		data: function() {
			return {
                active: false,
                timeoutReposition: null
            };
		},
        methods: {
            async handleClick() {
                this.onclick();
                clearTimeout(this.timeoutReposition);
                this.active = !this.active;
                if (this.active) {
                    await this.$nextTick();
                    this.repositionBody();
                }
            },
            handleClose() {
                this.active = false;
            },
            repositionBody() {
                const rect = this.$refs.body.getBoundingClientRect();
                this.$refs.body.style.right = "auto";
                if (rect.x + rect.width >= document.documentElement.clientWidth) {
                    this.$refs.body.style.right = 0;
                }
                this.timeoutReposition = setTimeout(this.repositionBody, 1000);
            }
        }
    }
</script>

<style lang="scss">

	@import "[client]/style/config.scss";

    .module {
        position: relative;

        .module-status {
            min-width: #{$client-menu-height}px;
            height: #{$client-menu-height}px;
            line-height: #{$client-menu-height}px;
            text-align: center;
            padding: 0 10px;
            white-space: nowrap;

            cursor: pointer;
            user-select: none;
            &:hover {
                background-color: #999;
            }
        }

        .module-body {
            position: absolute;

			color: $client-menu-color;
			background-color: $client-menu-background-color;

            top: #{$client-menu-height}px;

            .module-body-list {
                width: 100%;
                padding: 4px 10px;
                white-space: nowrap;

                cursor: pointer;
                user-select: none;
                &:hover {
                    background-color: #999;
                }
            }
        }
    }

</style>
