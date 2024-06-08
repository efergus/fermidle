<script lang="ts">
	import Frac from './Frac.svelte';
	import Question from './Question.svelte';
</script>

<div class="flex flex-col gap-2">
	<h2 class="mb-2">What is Fermidle?</h2>
	<p class="bold">Fermidle is a number-guessing game.</p>
	<p>
		You'll see a question, and your goal is to guess the <i>magnitude</i> of the answer in 6 tries or
		less. The questions will be hard, but you don't have to get them exactly right. You just have to
		get close enough.
	</p>
	<p>Here's an example:</p>
	<Question
		describe
		question={{
			question: '',
			answer: 3.4e-4,
			values: [
				{
					name: 'Height of the Eiffel Tower',
					value: '3.3e2 m1',
					image:
						'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/400px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg'
				},
				{
					name: 'Diameter of a Golf Ball',
					value: '4.1e-2 m1',
					image:
						'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Golfball.jpg/400px-Golfball.jpg'
				}
			]
		}}
		value={0}
	/>
	<p>
		Phrased another way, the question is "How many Golf Balls would it take to reach the top of the
		Eiffel Tower"? Pretty easy if you know both those values. But what if you don't? Well, we can
		make educated guesses and get close enough pretty quickly. Let's try.
	</p>

	<p class="bold">How tall is the Eiffel Tower?</p>
	<p>
		We can try guessing how many stories tall it is. I'd say probably bigger than 10 stories, but
		smaller than 100. Let's make a guess of 30 stories for now. A story is a little over 4 meters
		tall, so we'll guess that the Eiffel Tower is <i>30 · 4m = 120m</i> tall. In scientific notation
		that is <i>1.2e2m</i>.
	</p>
	<p class="bold">What is the diameter of a golf ball?</p>
	<p>
		I know about how big a golf ball is, I'll say it's about <i>3cm</i> in diameter. That's
		<i>3e-2m</i>.
	</p>
	<p class="bold">Answer</p>
	<p>
		From here, getting an answer is pretty easy. We just have to divide the tower height by the golf
		ball diameter.
	</p>
	<p><i>1.2e2m / 3e-2m = 4e3</i></p>
	<p>
		And there's our answer! We'll enter it as <i>3</i> because that is the magnitude of the answer.
		It turns out the true answer is closer to <i>7e3</i>, but since the magnitude is still 10<sup
			>3</sup
		>
		our answer of <i>3</i> is still correct.
	</p>

	<p>
		Ideally you'll do all this without a calculator. It's more fun to try to do these problems in
		your head, but I can't really stop you.
	</p>
	<p class="italic bold">Note: answers can be negative</p>
	<p>
		If the question was reversed, and we wanted the diameter of a golf ball divided by the height of
		the Eiffel Tower, our answer would be:
	</p>
	<p><i>3e-2m / 1.2e2m ≈ 3e-4</i></p>
	<p>Which means the final answer would actually be <i>-4</i></p>
	.
</div>

<style>
	i {
		font-family: serif;
	}

	p {
		padding-left: 1em;
	}
	p.bold {
		padding-left: 0px;
	}

	.bold {
		font-weight: bold;
	}
</style>
