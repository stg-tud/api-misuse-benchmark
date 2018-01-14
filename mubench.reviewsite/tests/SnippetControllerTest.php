<?php

use MuBench\ReviewSite\Controllers\SnippetsController;
use MuBench\ReviewSite\Models\Snippet;

require_once 'SlimTestCase.php';

class SnippetControllerTest extends SlimTestCase
{

    private $snippetController;


    function setUp()
    {
        parent::setUp();
        $this->snippetController = new SnippetsController($this->container);
    }

    function test_snippet_creation()
    {
        $this->snippetController->createSnippet('-p-', '-v-', '-code-', 10, '//src/file');
        $actualSnippet = Snippet::where(['project_muid' => '-p-', 'version_muid' => '-v-', 'snippet' => '-code-', 'line' => 10, 'file' => '//src/file'])->first();
        self::assertEquals('-p-', $actualSnippet->project_muid);
        self::assertEquals('-v-', $actualSnippet->version_muid);
        self::assertEquals('-code-', $actualSnippet->snippet);
        self::assertEquals(10, $actualSnippet->line);
        self::assertEquals('//src/file', $actualSnippet->file);
    }
}
