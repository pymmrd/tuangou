$(function(){$("#profile_city").focus(function(){$("#select_for_profile").show();}); $("#select_for_profile li a ").click(function(){var name = $(this).text(); $("#profile_city").val(name);$("#select_for_profile").hide();}); $("#mod_profile_submit").click(function(){var city = $("#profile_city").val(); if (!city){return false;}});});