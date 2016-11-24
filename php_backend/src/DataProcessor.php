<?php

use Monolog\Logger;

class DataProcessor {

	private $db;
	private $logger;

	function __construct(DBConnection $db, Logger $logger){
		$this->db = $db;
		$this->logger = $logger;
	}

	public function getMetadata($misuse){
		$query = $this->db->getMetadata($misuse);
		foreach($query as $q){
			$data = $q;
			$data['violation_types'] = explode('[;]', $q['violation_types']);
			return $data;
		}
	}

	public function getReview($user, $identifier){
		$query = $this->db->getReview($user, $identifier);
		foreach($query as $q){
			return $q;
		}
	}

	public function getPatterns($misuse){
		$query = $this->db->getPattern($misuse);
		foreach($query as $q){
			return $q;
		}
	}

	public function getHits($table, $project, $version, $misuse, $exp){
		$query = $this->db->getHits($table, $project, $version, $misuse, $exp);
		$result = [];
		foreach($query as $q){
			foreach($q as $key => $value){
				if($key !== "target_snippets" && strpos($value, ";") !== false){
					$q[$key] = explode('[;]', $value);
				}
			}
			$result[] = $q;
		}
		return $result;
	}
	
	public function getDatasets($prefix){
		return $this->getPrefixTable($prefix, 1);
	}

	public function getDetectors($prefix){
		return $this->getPrefixTable($prefix, 2);
	}

	public function getPrefixTable($prefix, $suffix){
		$tables = $this->db->getTables();
		$names = array();
		foreach($tables as $t){
			if(substr($t,0,strlen($prefix)) === $prefix){
				$new = explode('[_]', $t)[$suffix];
				$add = true;
				foreach($names as $n){
					if($n === $new){
						$add = false;
						break;
					}
				}
				if($add){
					$names[] = $new;
				}
			}
		}
		return $names;
	}

	public function getAllReviews($table, $project, $version, $id){
		$query = $this->db->getAllReviews($table . "_" . $project . "_" . $version . "_" . $id);
		$reviewer = [];
		foreach($query as $q){
			$reviewer[] = $q['name'];
		}
		return $reviewer;
	}

	public function getIndex($table, $exp){
		$stats = $this->db->getAllStats($table);
		$projects = [];
		foreach($stats as $s){
			foreach($this->db->getPotentialHits($table, $s['project'], $s['version']) as $hit){
				if($exp !== "ex2"){
					$meta = $this->getMetadata($hit['misuse']);
					$hit['violation_types'] = $meta['violation_types'];
				}
				$reviews = $this->getAllReviews($table, $s['project'], $s['version'], $exp === "ex2" ? $hit['id'] : $hit['misuse']);
				$hit['reviews'] = $reviews;
				$s['hits'][] = $hit;
			}
			$projects[$s['project']][] = $s;
		}
		return $projects;
	}

}