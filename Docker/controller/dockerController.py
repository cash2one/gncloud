# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify


# todo. Container 생성 및 실행
def doc_create():
    # todo doc_create 1. Docker Container를 생성한다.
    # todo doc_create 2. Docker Container 정보를 DB에 저장한다.
    return jsonify(status=False, message="미구현")


# todo. Container 상태변경
def doc_state():
    # todo doc_state 1. Docker Container의 상태를 수정한다.
    # todo doc_state 2. Docker Container 정보를 DB에 업데이트한다.
    return jsonify(status=False, message="미구현")


# todo. Container 삭제
def doc_delete():
    # todo doc_delete 1. 지정된 Docker Container를 삭제한다.
    return jsonify(status=False, message="미구현")


# todo. Container 정보
def doc_vm():
    return jsonify(status=False, message="미구현")


# todo. Container 리스트
def doc_vm_list():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 생성 및 업로드
def doc_new_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 삭제
def doc_delete_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 리스트
def doc_image_list():
    return jsonify(status=False, message="미구현")
