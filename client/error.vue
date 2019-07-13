<template>
	<div class="error" v-if="error">
        <div class="error-message">{{ message }}</div>
	</div>
</template>

<script>
	"use strict"

	export default {
        props: {
            error: {type: Error || String, required: false, default: null}
        },
		data: function() {
			return {};
		},
        computed: {
            message() {
                console.error(this.error);
                return String(this.error.message || this.error);
            }
        }
	}
</script>

<style lang="scss">
    .error {
        background-color: #a50303;
        color: white;
        padding: 10px 20px;
    }
</style>
